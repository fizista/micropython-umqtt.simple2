# ###############################
# A sample file to run the tests.
# ###############################

WIFI_SSID='<YOUR WIFI SSID>'
WIFI_PASSWORD='<YOUR WIFI PASSWORD>'

MQTT_BROKER_IP = '???' # or hostname
MQTT_BROKER_TEST_USER = 'test'
MQTT_BROKER_TEST_PASSWORD = 'abc'

CLIENT_CERT = '/client.crt.der'
CLIENT_KEY = '/client.key.der'

import machine
import utime
import network
from ubinascii import hexlify
import time

ap = network.WLAN(network.AP_IF)
ap.active(False)

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(WIFI_SSID, WIFI_PASSWORD)

for t in range(60):
    time.sleep(1)
    if sta.isconnected():
        break
    if sta.status() != network.STAT_CONNECTING:  # 1001
        break
else:
    print(sta.scan())
    raise Exception('WiFi Connection Timeout')

print('*****************')
print('* Connection OK *')
print('*****************')

import tests as tests_mod


def read_data(file_name: str):
    try:
        with open(file_name, 'rb') as f:
            data = f.read()
            if not data:
                raise Exception('No key data')
            return data
    except OSError:
        raise Exception('Problems when loading a file: %s' % file_name)


key_data = read_data(CLIENT_KEY)
cert_data = read_data(CLIENT_CERT)


class TestMQTT(tests_mod.TestMQTT):
    def disable_net(self):
        # Works with esp32 and esp8266 ports.
        # If it doesn't work with your port, please rewrite this part.
        wlan = network.WLAN(network.STA_IF)
        wlan.disconnect()
        for i in range(500):
            utime.sleep_ms(100)
            if not wlan.isconnected():
                return
        raise Exception('Network disconnection problem!')

    def enable_net(self):
        # Works with esp32 and esp8266 ports.
        # If it doesn't work with your port, please rewrite this part.
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            return
        try:
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        except:
            print('sta.status=', sta.status())
            raise
        for i in range(500):
            utime.sleep_ms(100)
            if wlan.isconnected():
                return
        raise Exception('Network connection failure!')

    def _print_net_stats(self, i_name: str, i):
        status = i.status()
        CFG_ITEMS = ('authmode', 'channel', 'dhcp_hostname', 'essid', 'hidden', 'hostname', 'key', 'mac', 'max_clients',
                     'reconnects', 'security', 'ssid', 'txpower')
        print('NET(%s): active=' % i_name, i.active())
        print('NET(%s): isconnected=' % i_name, i.isconnected())
        stat_names = [n for n in dir(network) if n.startswith('STAT_')]
        stats_map = dict([(getattr(network, sn), sn) for sn in stat_names])
        print('NET(%s): status=' % i_name, stats_map.get(status, status))
        print('NET(%s): ifconfig=' % i_name, i.ifconfig())
        for c in CFG_ITEMS:
            try:
                print('NET(%s): config(%s)=' % (i_name, c), i.config(c))
            except:
                pass

    def network_status(self):
        ap = network.WLAN(network.AP_IF)
        sta = network.WLAN(network.STA_IF)
        self._print_net_stats('AP', ap)
        self._print_net_stats('STA', sta)


# MQTT, anon, unencrypted, unauthenticated
tests = TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    MQTT_BROKER_IP,
    port=1883
)
t1 = tests.run(verbose=False)

# MQTT, password, unencrypted
tests = TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    MQTT_BROKER_IP,
    port=1884,
    user=MQTT_BROKER_TEST_USER,
    password=MQTT_BROKER_TEST_PASSWORD
)
t2 = tests.run(verbose=False)

# MQTT, encrypted, unauthenticated
# TestMQTT.HIDE_SENSITIVE = False
tests = TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    MQTT_BROKER_IP,
    port=8883,
    ssl=True,
    ssl_params={},
    keepalive=180,
    socket_timeout=120
)
t3 = tests.run(verbose=False)

# Encrypted MQTT, encrypted, client certificate required
tests = TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    MQTT_BROKER_IP,
    port=8884,
    ssl=True,
    ssl_params={'key': key_data, 'cert': cert_data, },
    keepalive=180,
    socket_timeout=120
)
t4 = tests.run(verbose=False)

# MQTT, encrypted, authenticated
# TestMQTT.HIDE_SENSITIVE = False
tests = TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    MQTT_BROKER_IP,
    port=8883,
    ssl=True,
    ssl_params={},
    user=MQTT_BROKER_TEST_USER,
    password=MQTT_BROKER_TEST_PASSWORD
)
t5 = tests.run(verbose=False)


def print_title(txt: str):
    print('TEST NAME: %s' % txt)


tt = (
    ('MQTT, anon, unencrypted, unauthenticated', t1),
    ('MQTT, password, unencrypted', t2),
    ('MQTT, encrypted, unauthenticated', t3),
    ('MQTT, encrypted, client certificate required', t4),
    ('MQTT, encrypted, authenticated', t5),
)

for k, v in tt:
    print_title(k)
    tests.verbose_tests(v)

for t_i, (t_group, t_val) in enumerate(tt):
    print('t_%d - %s' % (t_i, t_group))

print('')

print('%30s |' % 'Test name', end='')
for t_i, (t_group, t_val) in enumerate(tt):
    print('%8s-t_0 | ' % ('t_%d' % t_i), end='')
print()

for ktn, tn in enumerate(tests.TESTS):
    print('%30s |' % tn, end='')
    for t_i, (t_group, t_val) in enumerate(tt):

        status_base_test = tt[0][1][tests.TESTS[ktn]][0]
        time_base_test = tt[0][1][tests.TESTS[ktn]][1]
        status_current_test = t_val[tn][0]
        time_current_test = t_val[tn][1]

        if status_base_test:
            print(
                '%12s | ' % (str(abs(time_current_test - time_base_test)) + ' ms' if status_current_test else 'ERROR'),
                end='')
        else:
            print('%12s | ' % ('UNKNOWN ms' if status_current_test else 'ERROR'), end='')
    print()
print()
print('%30s |' % 'Test name', end='')
for t_i, (t_group, t_val) in enumerate(tt):
    print('%12s | ' % ('t_%d' % t_i), end='')
print()

for tn in tests.TESTS:
    print('%30s |' % tn, end='')
    for t_i, (t_group, t_val) in enumerate(tt):
        print('%12s | ' % (str(t_val[tn][1]) + ' ms ' if t_val[tn][0] else 'ERROR'), end='')
    print()

# A single test can be run with a command:
# tests.run_test('<test_name>')