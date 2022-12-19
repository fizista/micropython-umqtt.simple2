.. role:: bash(code)
   :language: bash

.. role:: python(code)
   :language: python

umqtt.simple2
=============

umqtt.simple2_ is a MQTT client for MicroPython. (Note that it uses some
MicroPython shortcuts and doesn't work with CPython).

Support MQTT Version 3.1.1 only.

It certainly works with micropython ports: esp8266 and esp32. It should also
work with other ports, but the library was not tested under other ports.

MQTT client with more features
------------------------------

There's a separate umqtt.robust2_  module which builds
on umqtt.simple2_ adds the ability to reconnect.
It is able to send unsent messages itself. And many more...

Differences between umqtt.simple and umqtt.simple2
--------------------------------------------------
* When sending messages from QoS=1, there is no problem with "suspending"
  the script while waiting for confirmation of message receipt by the server.
* When subscribing to a channel, there is no problem with "suspending"
  the script while waiting for confirmation of the subscription by the server.
* Information about receiving or failing to receive a message from QoS=1 or subscription
  can only be received by registering a callback using the :python:`set_callback_status()` method.
* Currently, the module informs about errors in more detailed way. See the umqtt/errno.py file.
* The application should also not hang up when using :python:`check_msg()`
* The code compiled for MPY files, is about 30% larger than the original one.
  So this library has gained more functionality (maybe reliability),
  but this was done at the expense of the amount of code.

Problems and solutions
----------------------
* ImportError: no module named 'umqtt.simple2'

  Versions of micropython from http://micropython.org/download/ since version 1.12 include
  the umqtt library, which conflicts with the current library.
  To avoid conflicts, you need to change the order of importing libraries.
  You need to import the '/lib' libraries first and then the system libraries.
  Just add the following lines of code to the boot.py file:

.. code-block:: python

    import sys
    sys.path.reverse()

How and where to install this code?
-----------------------------------
You can install using the upip:

.. code-block:: python

    import upip
    upip.install("micropython-umqtt.simple2")

or

.. code-block:: bash

    micropython -m upip install -p modules micropython-umqtt.simple2


You can also clone this repository, and install it manually:

.. code-block:: bash

    git clone https://github.com/fizista/micropython-umqtt.simple2.git

Manual installation gives you more possibilities:

* You can compile this library into MPY files using the :bash:`compile.sh` script.
* You can remove comments from the code with the command: :bash:`python setup.py minify`
* You can of course copy the code as it is, if you don't mind.

**Please note that the PyPi repositories contain optimized code (no comments).**

Design requirements
-------------------

* Memory efficiency.
* Avoid infamous design anti-patterns like "callback hell".
* Support for both publishing and subscription via a single client
  object (another alternative would be to have separate client classes
  for publishing and subscription).

API design
----------

Based on the requirements above, there are following API traits:

* All data related to MQTT messages is encoded as bytes. This includes
  both message content AND topic names (even though MQTT spec states
  that topic name is UTF-8 encoded). The reason for this is simple:
  what is received over network socket is binary data (bytes) and
  it would require extra step to convert that to a string, spending
  memory on that. Note that this applies only to topic names (because
  they can be both sent and received). Other parameters specified by
  MQTT as UTF-8 encoded (e.g. ClientID) are accepted as strings.
* Subscribed messages are delivered via a callback. This is to avoid
  using a queue for subscribed messages, as otherwise they may be
  received at any time (including when client expects other type
  of server response, so there're 2 choices: either deliver them
  immediately via a callback or queue up until an "expected" response
  arrives). Note that lack of need for a queue is delusive: the
  runtime call stack forms an implicit queue in this case. And unlike
  explicit queue, it's much harder to control. This design was chosen
  because in a common case of processing subscribed messages it's
  the most efficient. However, if in subscription callback, new
  messages of QoS>0 are published, this may lead to deep, or
  infinite recursion (the latter means an application will terminate
  with :python:`RuntimeException`).

API reference
-------------

Taking into account API traits described above, umqtt pretty closely
follows MQTT control operations, and maps them to class methods:

* ``connect(...)`` - Connect to a server. Returns True if this connection
  uses persisten session stored on a server (this will be always False if
  clean_session=True argument is used (default)).
* ``disconnect()`` - Disconnect from a server, release resources.
* ``ping()`` - Ping server (response is processed automatically by wait_msg()).
* ``publish()`` - Publish a message.
* ``subscribe()`` - Subscribe to a topic.
* ``set_callback()`` - Set callback for received subscription messages. call(topic, msg, retained)
* ``set_callback_status()`` - Set callback for received subscription messages. call(pid, status)
* ``set_last_will()`` - Set MQTT "last will" message. Should be called
  *before* connect().
* ``wait_msg()`` - Wait for a server message. A subscription message will be
  delivered to a callback set with set_callback(), any other messages
  will be processed internally.
* ``check_msg()`` - Check if there's pending message from server. If yes,
  process the same way as wait_msg(), if not, return immediately.

``wait_msg()`` and ``check_msg()`` are "main loop iteration" methods, blocking
and non-blocking version. They should be called periodically in a loop,
``wait_msg()`` if you don't have any other foreground tasks to perform
(i.e. your app just reacts to subscribed MQTT messages), ``check_msg()``
if you process other foreground tasks too.

Note that you don't need to call ``wait_msg()``/``check_msg()`` if you only
publish messages with QoS==0, never subscribe to them.

If you are using a subscription and/or sending QoS>0 messages, you must run one of these
commands ( ``wait_msg()`` or ``check_msg()`` ).

**For more detailed information about API please see the source code
(which is quite short and easy to review) and provided examples.**


Supported MQTT features
-----------------------

QoS 0 and 1 are supported for both publish and subscribe. QoS2 isn't
supported to keep code size small. Besides ClientID, only "clean
session" parameter is supported for connect as of now.

Simple library testing
----------------------
The current tests are not only to test the code, but also to check it in a real environment. Therefore, a good idea,
before we use this library in our own project, is to test its operation with the MQTT broker.

To test if the library works well with your device and MQTT broker,
use the TestMQTT class from the `tests.py` module.

If you don't have your own MQTT broker yet, you can use the free MQTT test broker (test.mosquitto.org).

There is also a sample file `main.py`(`example_test_main.py`),
In this file we add only network configuration. Upload this file to your device with umqtt.simple2_
library and `tests.py` module. Then reset the device and watch the results in the console.

How to get tests up and running quickly:

.. code-block:: bash

    cp example_test_main.py main.py

In the main.py file, assign the appropriate values from your WiFi network to the WIFI_SSID
and WIFI_PASSWORD variables.

.. code-block:: bash

    ./upload_to_device.sh

or

.. code-block:: bash

    ./upload_to_device.sh yes # A compiled version that takes up less memory on devices.

Launching the tests:

.. code-block:: bash

    screen /dev/ttyUSB0  115200 # or screen /dev/ttyACM0  115200
    # Ctrl+D - to restart device


Configuring an encrypted connection with test.mosquitto.org:

.. code-block:: bash

    openssl genrsa -out client.key
    openssl req -out client.csr -key client.key -new
    cat client.csr # Copy and paste on the page: https://test.mosquitto.org/ssl/ , click "submit"
    # Save the certificate to the same directory as client.crt
    # Dowlnoad mosquitto.org.crt
    # Change key formats:
    openssl x509 -in client.crt -out client.crt.der -outform DER
    openssl rsa -in client.key -out client.key.der -outform DER
    openssl x509 -in mosquitto.org.crt -out mosquitto.org.crt.der -outform DER
    # Upload to device
    ampy -d1 --baud 115200 --port /dev/ttyACM0 put ./client.key.der
    ampy -d1 --baud 115200 --port /dev/ttyACM0 put ./client.crt.der
    ampy -d1 --baud 115200 --port /dev/ttyACM0 put ./mosquitto.org.crt.der

Configuring keys for MQTT server(eg. mosquitto):

.. code-block:: bash

    openssl genrsa -des3 -out ca.key 2048
    openssl req -new -x509 -days 1826 -key ca.key -out ca.crt
    openssl genrsa -out server.pem 2048
    openssl req -new -out server.csr -key server.pem
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out cert.der -days 360
    openssl rsa -inform pem -in server.pem -outform der -out key.der


Different problems
------------------
* Wrong topic format during subscription - you'll get `OSError: [Errno 104] ECONNRESET` in subscribe()
  or `MQTTException: 1` in the `wait_msg()/check_msg()`

Additional resources
--------------------
* https://mosquitto.org/ - Eclipse Mosquitto is an open source  message broker that implements the MQTT protocol.
* https://test.mosquitto.org/ - MQTT test server
* http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html - MQTT 3.1.1 specyfication
* https://flespi.com/tools/mqtt-board - An open-source MQTT client tool for easy MQTT pub/sub, testing, and demonstration.
* https://github.com/wialon/gmqtt - Python MQTT client implementation(not for the micropython)
* https://www.hivemq.com/mqtt-essentials/ - Blog with explanation of MQTT specifications

.. _umqtt.simple2: https://github.com/fizista/micropython-umqtt.simple2
.. _umqtt.robust2: https://github.com/fizista/micropython-umqtt.robust2