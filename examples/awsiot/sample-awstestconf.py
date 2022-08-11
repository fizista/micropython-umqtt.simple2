# Configuration parameters for awstest
# example use:
#from awstestconf import SSID,WIFIPASS,CLIENT_ID,AWS_ENDPOINT,TOPIC,KEYFILE,CERTFILE

# wifi parameters
SSID='WIFI_NAME'
WIFIPASS='WIFI_PASS'

# AWS IOT parameters
AWS_ENDPOINT = b'HOST.iot.REGION.amazonaws.com'
CLIENT_ID = "basicPubSub"  # Should be unique for each device connected.
TOPIC = "sdk/test/Python"
KEYFILE = "/certs/newthing.private.der"
CERTFILE = "/certs/newthing.cert.der"

# About the aws iot credentials:
#
# The certificate and private key files must be in der i.e. binary format.
#
# To covert the pem files supplied by AWS:
#   openssl x509 -in newthing.cert.pem -out newthing.cert.def -outform DER
#   openssl rsa -in newthing.private.key -out newthing.private.der -outform DER
#
# To test certs from another system:
#    openssl s_client -connect host.iot.region.amazonaws.com:8443 \
#    -cert certificate.pem.crt -key private.pem.key [-CAfile AmazonRootCA1.pem]
# -CAfile is optional since we don't use it here either
