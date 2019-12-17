import utime
from ubinascii import hexlify
from umqtt.simple2 import MQTTClient as _MQTTClient, MQTTException


def debug_print(data):
    print('HEX: %s STR: /*' % hexlify(data).decode('ascii'), end='')
    for i, d in enumerate(data):
        if type(d) == str:
            d = ord(d)
        if d > 31 and d not in (127, 144):
            print(chr(d), end='')
        else:
            print('.', end='')
    print('*/')


class MQTTClient(_MQTTClient):

    def _read(self, n):
        out = super()._read(n)
        if type(out) == bytes:
            debug_print(out)
        else:
            print('READ: %s' % out)
        return out

    def _write(self, bytes_wr, length=0):
        debug_print(bytes_wr)
        return super()._write(bytes_wr, length)


class TestMQTT:
    def __init__(self, *args, **kwargs):
        print('MQTT connection args:', args, kwargs)
        self.client = MQTTClient(*args, **kwargs)
        self.msg_id = args[0]
        self.client.set_callback(self.sub_cb)
        self.client.set_callback_status(self.stat_cb)
        self.subsctiption_out = None
        self.status_out = None
        # self.client.set_callback(self.sub_cb)
        # self.client.connect()
        # self.client.subscribe(b"foo_topic")

    def sub_cb(self, topic, msg, retained):
        print('TOPIC: %s MSG: %s R: %s' % (topic, msg, retained))
        self.subsctiption_out = (topic, msg, retained)

    def stat_cb(self, pid, status):
        print('PID: %s STATUS: %d' % (pid, status))
        self.status_out = (pid, status)

    def get_subscription_out(self, timeout=5):
        for i in range(timeout):
            self.client.check_msg()
            if self.subsctiption_out != None:
                o = self.subsctiption_out
                return o
            utime.sleep(1)
        raise Exception('timeout')

    def get_status_out(self, timeout=5):
        for i in range(timeout):
            self.client.check_msg()
            if self.status_out != None:
                o = self.status_out
                self.status_out = None
                return o
            utime.sleep(1)
        raise Exception('timeout')

    def disable_net(self):
        pass

    def enable_net(self):
        pass

    def get_topic(self, test_name):
        return '%s/umqtt.simple2/%s/' % (self.msg_id, test_name)

    def run(self):
        test_fails = []
        tests = [
            'test_publish_qos_0',
            'test_subscribe_qos_0',
            'test_subscribe_qos_1',
            'test_subscribe_qos_2',
            'test_subscribe_long_topic',
            'test_publish_qos_1',
            'test_publish_qos_2',
            'test_publish_retain',
        ]
        for test_name in tests:
            if not self.run_test(test_name):
                test_fails.append(test_name)
        if test_fails:
            print('\nTests fails: %s\n' % ', '.join(test_fails))
        else:
            print('All the tests were finished successfully!')

    def run_test(self, test_name):
        self.subsctiption_out = None
        self.status_out = None
        test = getattr(self, test_name)
        print('RUN [%s]' % test_name)
        test_pass = True
        try:
            test(self.get_topic(test_name))
        except Exception as e:
            from sys import print_exception
            print_exception(e)
            test_pass = False
        print('END [%s] %s\n' % (test_name, 'succes' if test_pass else 'FAIL'))
        return test_pass

    def test_publish_qos_0(self, topic):
        self.client.connect()
        self.client.publish(topic, 'test QoS 0')
        self.client.disconnect()

    def test_publish_qos_1(self, topic):
        self.client.connect()
        pid = self.client.publish(topic, 'test QoS 1', qos=1)
        out_pid, status = self.get_status_out()
        assert pid == out_pid
        assert status == 1
        self.client.disconnect()

    def test_publish_qos_2(self, topic):
        self.client.connect()
        try:
            self.client.publish(topic, 'test QoS 2', qos=2)
        except MQTTException as e:
            print(e)
        self.client.disconnect()

    def test_publish_retain(self, topic):
        self.client.connect()
        pid = self.client.publish(topic, 'test retain', qos=1, retain=True)
        self.client.disconnect()
        self.client.connect()
        self.client.subscribe(topic + '#')
        t, m, r = self.get_subscription_out()
        assert t.decode('ascii') == topic
        assert m.decode('ascii') == 'test retain'
        assert r == True
        self.client.disconnect()

    def test_subscribe_qos_0(self, topic):
        self.client.connect()
        self.client.subscribe(topic + '#')
        msg_in = 'abc123'
        self.client.publish(topic, msg_in, qos=1)
        msg_out = self.get_subscription_out()[1]
        assert msg_in == msg_out.decode('ascii')
        self.client.disconnect()

    def test_subscribe_qos_1(self, topic):
        pass

    def test_subscribe_qos_2(self, topic):
        pass

    def test_subscribe_long_topic(self, topic):
        self.client.connect()
        topic += '1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/1234567890/'
        self.client.subscribe(topic + '#')
        msg_in = 'abc123'
        self.client.publish(topic, msg_in, qos=1)
        msg_out = self.get_subscription_out()[1]
        assert msg_in == msg_out.decode('ascii')
        self.client.disconnect()
