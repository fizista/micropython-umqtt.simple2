import machine
import time
import network
from umqtt.simple2 import MQTTClient
# next must be created from sample-awstestconf.py
from awstestconf import SSID,WIFIPASS,CLIENT_ID,AWS_ENDPOINT,TOPIC,KEYFILE,CERTFILE

print('WiFi name:', SSID)

key = open(KEYFILE,'rb').read()
cert = open(CERTFILE,'rb').read()

# SSL certificates.
ssl_params = {'key': key, 'cert': cert}

# Setup WiFi connection.
wlan = network.WLAN( network.STA_IF )
wlan.active( True )
wlan.connect( SSID, WIFIPASS )

while not wlan.isconnected():
  time.sleep(1)
print('ifconfig:', wlan.ifconfig())

def msg_received(topic, msg, retained, duplicate):
    print("Received:", msg, "Topic:", topic)

seq = {'v':0}

def mypublish():
  seq['v'] = seq['v']+1
  msg = '{"message":"hello world","sequence":%d}' % (seq['v'])
  mqtt.publish( topic = TOPIC, msg = msg, qos = 0 )

# Connect to MQTT broker.
mqtt = MQTTClient(  CLIENT_ID, AWS_ENDPOINT, \
                    port = 8883, keepalive = 10000, \
                    ssl = True, ssl_params = ssl_params )
mqtt.connect()
mqtt.set_callback(msg_received)
mqtt.subscribe(TOPIC)
print("Subscribed to", TOPIC)
mqtt.check_msg()
# Without the next delay, we may not receive the first publish
time.sleep(0.25)
print("Publishing first message to", TOPIC)
mypublish()
pubcnt = 30  # number to publish
pubint = 2000 # msec between pubs
print("Publishing %d messages, %d msec between each" % (pubcnt, pubint))
cnt = 1 # (already sent 1)
while cnt <= pubcnt:
    cnt += 1
    start_ms = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_ms) < pubint:
      mqtt.check_msg()
    mypublish()