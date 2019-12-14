EUNKNOWN = -1   # Unknown
ECONCLOSE = 1   # Connection closed by host
EREADLEN = 2    # Wrong length of read data
EWRITELEN = 3   # Wrong length of read data
ESTRTOLONG = 4  # String too long
EUNKNOWNPID = 5 # A "PID" was received that was not sent.
ERESPONSE = 6   # Wrong response
ELOCK = 10      # Currently, the MQTT client is blocked. It is probably waiting for an answer.
                # The lock will be removed when the customer receives a response.
EUNIMPLEMENTED = 100
