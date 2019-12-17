# ###
# <<< Add the network initiation code to your device here.>>>
# ###
import machine
import utime
from ubinascii import hexlify

utime.sleep(2)

import tests as tests_mod

# 1883 : MQTT, unencrypted
# 8883 : MQTT, encrypted
# 8884 : MQTT, encrypted, client certificate required
tests = tests_mod.TestMQTT(
    hexlify(machine.unique_id()).decode('ascii'),
    'test.mosquitto.org',
    port=1883
)

tests.run()

# A single test can be run with a command:
# tests.run_test('<test_name>')
