# ###
# <<< Add the network initiation code to your device here.>>>
# ###
import machine
import utime
import network
from ubinascii import hexlify

utime.sleep(2)

import tests as tests_mod


class TestMQTT(tests_mod.TestMQTT):
    def disable_net(self):
        # Works with esp32 and esp8266 ports.
        # If it doesn't work with your port, please rewrite this part.
        wlan = network.WLAN(network.STA_IF)
        wlan.disconnect()
        for _ in range(500):
            utime.sleep_ms(100)
            if not wlan.isconnected():
                return
        raise Exception('Network disconnection problem!')

    def enable_net(self):
        # Works with esp32 and esp8266 ports.
        # If it doesn't work with your port, please rewrite this part.
        wlan = network.WLAN(network.STA_IF)
        wlan.connect()
        for _ in range(500):
            utime.sleep_ms(100)
            if wlan.isconnected():
                return
        raise Exception('Network connection failure!')


# 1883 : MQTT, unencrypted
# 8883 : MQTT, encrypted
# 8884 : MQTT, encrypted, client certificate required
tests = TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    'test.mosquitto.org',
    port=1883
)

tests.run()

# A single test can be run with a command:
# tests.run_test('<test_name>')
