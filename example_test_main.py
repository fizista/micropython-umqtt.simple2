# ###############################
# A sample file to run the tests.
# ###############################

WIFI_SSID='<YOUR WIFI SSID>'
WIFI_PASSWORD='<YOUR WIFI PASSWORD>'

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
        print(f'NET({i_name}): active=', i.active())
        print(f'NET({i_name}): isconnected=', i.isconnected())
        stat_names = [n for n in dir(network) if n.startswith('STAT_')]
        stats_map = dict([(getattr(network, sn), sn) for sn in stat_names])
        print(f'NET({i_name}): status=', stats_map.get(status, status))
        print(f'NET({i_name}): ifconfig=', i.ifconfig())
        for c in CFG_ITEMS:
            try:
                print(f'NET({i_name}): config({c})=', i.config(c))
            except:
                pass

    def network_status(self):
        ap = network.WLAN(network.AP_IF)
        sta = network.WLAN(network.STA_IF)
        self._print_net_stats('AP', ap)
        self._print_net_stats('STA', sta)


# 1883 : MQTT, unencrypted
# 8883 : MQTT, encrypted
# 8884 : MQTT, encrypted, client certificate required

# tests = TestMQTT(
#     hexlify(machine.unique_id()).decode('ascii'),
#     'test.mosquitto.org',
#     port=1883
# )

# OR

# with open('/client.key.der', 'r') as f:
#     key_data = f.read()
#
# with open('/client.crt.der', 'r') as f:
#     cert_data = f.read()
#
# tests = TestMQTT(
#     hexlify(machine.unique_id()).decode('ascii'),
#     'test.mosquitto.org',
#     port=8884,
#     ssl=True,
#     ssl_params={'key': key_data, 'cert': cert_data, },
#     keepalive=180,
#     socket_timeout=120
# )

tests.run()

# A single test can be run with a command:
# tests.run_test('<test_name>')
