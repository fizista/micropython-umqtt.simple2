import usocket as socket
import ustruct as struct
from utime import ticks_add, ticks_ms, ticks_diff


class MQTTException(Exception):
    pass


def pid_gen(pid=0):
    while True:
        pid = pid + 1 if pid < 65535 else 1
        yield pid


class MQTTClient:

    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0,
                 ssl=False, ssl_params={}, socket_timeout=1, message_timeout=5):
        """
        Default constructor, initializes MQTTClient object.

        :param client_id:  Unique MQTT ID attached to client.
        :type client_id: str
        :param server: MQTT host address.
        :type server str
        :param port: MQTT Port, typically 1883. If unset, the port number will default to 1883 of 8883 base on ssl.
        :type port: int
        :param user: Username if your server requires it.
        :type user: str
        :param password: Password if your server requires it.
        :type password: str
        :param keepalive:
        :param ssl: Require SSL for the connection.
        :type ssl: bool
        :param ssl_params: Required SSL parameters.
        :type ssl_params: dict
        :param socket_timeout: The time in seconds after which the socket interrupts the connection to the server when no data exchange takes place.
        :type ssl_params: int
        :param message_timeout: The time in seconds after which the library recognizes that a message with QoS=1 or topic subscription has not been received by the server.
        :type ssl_params: int
        """
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.newpid = pid_gen()
        self.cb = None
        self.cbstat = lambda p, s: None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False
        self.rcv_pids = {}  # PUBACK and SUBACK pids awaiting ACK response

        self.last_rx = ticks_ms()  # Time of last communication from broker
        self.last_rcommand = ticks_ms()  # Time of last OK read command

        self.socket_timeout = socket_timeout
        self.message_timeout = message_timeout

    def _read(self, n):
        """
        Private class method.

        :param n: Expected length of read bytes
        :type n: int
        :return:
        """
        # in non-blocking mode, may not download enough data
        msg = self.sock.read(n)
        if msg == b'':  # Connection closed by host (?)
            raise MQTTException(1)
        if msg is not None:
            if len(msg) != n:
                raise MQTTException(2)
            self.last_rx = ticks_ms()
        return msg

    def _write(self, bytes_wr, length=0):
        """
        Private class method.

        :param bytes_wr: Bytes sequence for writing
        :type bytes_wr: bytes
        :param length: Expected length of write bytes
        :type n: int
        :return:
        """
        # In non-blocking socket mode, the entire block of data may not be sent.
        if length:
            bytes_wr = bytes_wr[:length]
        write_bytes = self.sock.write(bytes_wr)
        if write_bytes != len(bytes_wr):
            raise MQTTException(3)
        return write_bytes

    def _send_str(self, s):
        """
        Private class method.
        :param s:
        :type s: str
        :return: None
        """
        self._write(struct.pack("!H", len(s)))
        self._write(s)

    def _recv_len(self):
        """
        Private class method.
        :return:
        :rtype int
        """
        n = 0
        sh = 0
        while 1:
            b = self._read(1)[0]
            n |= (b & 0x7f) << sh
            if not b & 0x80:
                return n
            sh += 7

    def set_callback(self, f):
        """
        Set callback for received subscription messages.

        :param f: callable(topic, msg, retained)
        """
        self.cb = f

    def set_callback_status(self, f):
        """
        Set the callback for information about whether the sent packet (QoS=1)
        or subscription was received or not by the server.

        :param f: callable(pid, status)

        Where:
            status = 0 - timeout
            status = 1 - successfully delivered
            status = 2 - Unknown PID. It is also possible that the PID is outdated,
                         i.e. it came out of the message timeout.
        """
        self.cbstat = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        """
        Sets the last will and testament of the client. This is used to perform an action by the broker
        in the event that the client "dies".
        Learn more at https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/

        :param topic: Topic of LWT. Takes the from "path/to/topic"
        :type topic: str
        :param msg: Message to be published to LWT topic.
        :type msg: str
        :param retain: Have the MQTT broker retain the message.
        :type retain: bool
        :param qos: Sets quality of service level. Accepts values 0 to 2. PLEASE NOTE qos=2 is not actually supported.
        :type qos: int
        :return: None
        """
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        """
        Establishes connection with the MQTT server.

        :param clean_session: Starts new session on true, resumes past session if false.
        :type clean_session: bool
        :return: Existing persistent session of the client from previous interactions.
        :rtype: bool
        """
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\x04MQTT\x04\x02\0\0")

        sz = 10 + 2 + len(self.client_id)

        msg[7] = bool(clean_session) << 1
        # Clean session = True, remove current session
        if bool(clean_session):
            self.rcv_pids.clear()
        if self.user is not None:
            sz += 2 + len(self.user) + 2 + len(self.pswd)
            msg[6] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[7] |= self.keepalive >> 8
            msg[8] |= self.keepalive & 0x00FF
        if self.lw_topic:
            sz += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[6] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[6] |= self.lw_retain << 5

        i = 1
        while sz > 0x7f:
            premsg[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz

        self._write(premsg, i + 2)
        self._write(msg)
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user is not None:
            self._send_str(self.user)
            self._send_str(self.pswd)
        resp = self._read(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            if resp[3] >=1 and resp[3] <= 5:
                raise MQTTException(20 + resp[3])
            else:
                raise MQTTException(20, resp[3])
        return resp[2] & 1 # Is existing persistent session of the client from previous interactions.

    def disconnect(self):
        """
        Disconnects from the MQTT server.
        :return: None
        """
        self._write(b"\xe0\0")
        self.sock.close()

    def ping(self):
        """
        Pings the MQTT server.
        :return: None
        """
        self._write(b"\xc0\0")

    def publish(self, topic, msg, retain=False, qos=0, dup=False):
        """
        Publishes a message to a specified topic.

        :param topic: Topic you wish to publish to. Takes the form "path/to/topic"
        :type topic: str
        :param msg: Message to publish to topic.
        :type msg: str
        :param retain: Have the MQTT broker retain the message.
        :type retain: bool
        :param qos: Sets quality of service level. Accepts values 0 to 2. PLEASE NOTE qos=2 is not actually supported.
        :type qos: int
        :param dup: Duplicate delivery of a PUBLISH Control Packet
        :type dup: bool
        :return: None
        """
        if qos == 2:
            raise MQTTException(100)
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain | int(dup) << 3
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        if sz >= 2097152:
            raise MQTTException(4)
        i = 1
        while sz > 0x7f:
            pkt[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        self._write(pkt, i + 1)
        self._send_str(topic)
        if qos > 0:
            pid = next(self.newpid)
            struct.pack_into("!H", pkt, 0, pid)
            self._write(pkt, 2)
        self._write(msg)
        if qos > 0:
            self.rcv_pids[pid] = ticks_add(ticks_ms(), self.message_timeout * 1000)
            return pid

    def subscribe(self, topic, qos=0):
        """
        Subscribes to a given topic.

        :param topic: Topic you wish to publish to. Takes the form "path/to/topic"
        :type topic: str
        :param qos: Sets quality of service level. Accepts values 0 to 2. PLEASE NOTE qos=2 is not actually supported.
        :type qos: int
        :return: None
        """
        assert self.cb is not None, "Subscribe callback is not set"
        pkt = bytearray(b"\x82\0\0\0")
        pid = next(self.newpid)
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, pid)
        self._write(pkt)
        self._send_str(topic)
        self._write(qos.to_bytes(1, "little"))  # maksymalna wartość QOS jaką może nadawać serwer do klienta
        self.rcv_pids[pid] = ticks_add(ticks_ms(), self.message_timeout * 1000)
        return pid

    def _message_timeout(self):
        curr_tick = ticks_ms()
        for pid, timeout in self.rcv_pids.items():
            if ticks_diff(timeout, curr_tick) <= 0:
                self.rcv_pids.pop(pid)
                self.cbstat(pid, 0)

    def wait_msg(self, _st=None):
        """
        This method waits for a message from the server.

        It processes such messages:
        - response to PING
        - messages from subscribed topics that are processed by functions set by the set_callback method.
        - reply from the server that he received a QoS=1 message or subscribed to a topic

        :return: None
        """
        res = self._read(1)  # Throws OSError on WiFi fail
        # Real mode without blocking
        self.sock.settimeout(_st)
        if res is None:
            self._message_timeout()
            return None
        if res == b"\xd0":  # PINGRESP
            sz = self._read(1)[0]
            self.last_rcommand = ticks_ms()
            return

        op = res[0]

        if op == 0x40:  # PUBACK
            sz = self._read(1)
            if sz != b"\x02":
                raise MQTTException(-1)
            rcv_pid = self._read(2)
            pid = rcv_pid[0] << 8 | rcv_pid[1]
            if pid in self.rcv_pids:
                self.last_rcommand = ticks_ms()
                self.rcv_pids.pop(pid)
                self.cbstat(pid, 1)
            else:
                self.cbstat(pid, 2)

        if op == 0x90:  # SUBACK
            resp = self._read(4)
            if resp[3] == 0x80:
                raise MQTTException(-1)
            pid = resp[2] | (resp[1] << 8)
            if pid in self.rcv_pids:
                self.last_rcommand = ticks_ms()
                self.rcv_pids.pop(pid)
                self.cbstat(pid, 1)
            else:
                raise MQTTException(5)

        self._message_timeout()

        if op & 0xf0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self._read(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self._read(topic_len)
        sz -= topic_len + 2
        if op & 6:
            pid = self._read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self._read(sz)
        retained = op & 0x01
        self.cb(topic, msg, bool(retained))
        self.last_rcommand = ticks_ms()
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")  # Send PUBACK
            struct.pack_into("!H", pkt, 2, pid)
            self._write(pkt)
        elif op & 6 == 4:
            raise MQTTException(-1)

    def check_msg(self):
        """
        Checks whether a pending message from server is available.
        If not, returns immediately with None. Otherwise, does
        the same processing as wait_msg.

        :return: None
        """
        self.sock.setblocking(False)
        return self.wait_msg(_st=self.socket_timeout)
