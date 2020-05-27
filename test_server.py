# Connection example:
# telnet localhost 10000
#
import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def to_err(text, end='\n'):
    sys.stderr.write(text + end)
    sys.stderr.flush()


server_address = ('0.0.0.0', 10000)
sock.bind(server_address)
to_err('starting up on %s port %s' % sock.getsockname())
sock.listen(1)

try:
    while True:
        to_err('Waiting for a connection...')
        connection, client_address = sock.accept()
        try:
            to_err('┌ client connected: %s:%d' % client_address)
            while True:
                to_err('| operation type (r|w|c):', end='')
                operation = input().lower()
                if operation in ('r', 'read'):
                    data = connection.recv(16)
                    to_err('├ received "%s"' % data)
                elif operation in ('w', 'write'):
                    to_err('├ send data:')
                    data = input().encode('utf8')
                    connection.sendall(data)
                else:
                    break
        finally:
            connection.close()
            to_err('└ client disconnected')
except KeyboardInterrupt:
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
