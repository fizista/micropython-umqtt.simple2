EUNKNOWN = -1   # Unknown
ECONCLOSE = 1   # Connection closed by host
EREADLEN = 2    # Wrong length of read data
EWRITELEN = 3   # Wrong length of read data
ESTRTOLONG = 4  # String too long !!!!
ERESPONSE = 6   # Wrong response
ELOCK = 10      # Currently, the MQTT client is blocked. It is probably waiting for an answer.
                # The lock will be removed when the customer receives a response.
ECONUNKNOWN = 20     # Connection refused, unknown error
ECONPROTOCOL = 21    # Connection refused, unacteptable protocol version
ECONREJECT = 22      # Connection refused, identifier rejected
ECONUNAVAIBLE = 23   # Connection refused, server unavaible
ECONCREDENTIALS = 24 # Connection refused, bad credentials
ECONAUTH = 25        # Connection refused, not authorized

ESUBACKUNKNOWN = 40  # Subscribe confirm unknown fail, SUBACK
ESUBACKFAIL = 44     # Subscribe confirm response: Failure

EUNIMPLEMENTED = 100

# Status code numbers from set_callback_status()
STIMEOUT = 0    # timeout
SDELIVERED = 1  # successfully delivered
SUNKNOWNPID = 2 # Unknown PID. It is also possible that the PID is outdated,
                # i.e. it came out of the message timeout.