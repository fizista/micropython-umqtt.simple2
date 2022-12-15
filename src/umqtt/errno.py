EUNKNOWN = -1   # Unknown
ECONCLOSE = 1   # Connection closed by host
EREADLEN = 2    # Wrong length of read data
EWRITELEN = 3   # Wrong length of write data
ESTRTOLONG = 4  # String too long !!!!
ERESPONSE = 6   # Wrong response
EKEEPALIVE = 7  # Connection keep time has been exceeded (umqtt.robust2)
ENOCON = 8      # No connection

ECONUNKNOWN = 20     # Connection refused, unknown error
ECONPROTOCOL = 21    # Connection refused, unacteptable protocol version
ECONREJECT = 22      # Connection refused, identifier rejected
ECONUNAVAIBLE = 23   # Connection refused, server unavaible
ECONCREDENTIALS = 24 # Connection refused, bad credentials
ECONAUTH = 25        # Connection refused, not authorized
ECONNOT = 28         # No connection
ECONLENGTH = 29      # Connection, control packet type, Remaining Length != 2
ECONTIMEOUT = 30     # Connection timeout

ESUBACKUNKNOWN = 40  # Subscribe confirm unknown fail, SUBACK
ESUBACKFAIL = 44     # Subscribe confirm response: Failure

# Status code numbers from set_callback_status()
STIMEOUT = 0    # timeout
SDELIVERED = 1  # successfully delivered
SUNKNOWNPID = 2 # Unknown PID. It is also possible that the PID is outdated,
                # i.e. it came out of the message timeout.

