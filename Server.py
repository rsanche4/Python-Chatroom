import socket
import _thread
import sys
from cryptography.fernet import Fernet

if (len(sys.argv) != 3):
    print(f"Usage: {sys.argv[0]} IP PORT")
    print(f"Example: {sys.argv[0]} 192.168.163.128 8080")
    sys.exit(0)

KEY = b'Q9w1t3JpGXzGwTymwo1DhN6pX0H2CRWHhLPSNcv_U7I='
f = Fernet(KEY)

class Server():

    def __init__(self, ip, port):

        # For remembering users
        self.ipaddress = ip
        self.portaddress = port
        self.users_table = {}

        # Create a TCP/IP socket and bind it the Socket to the port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (self.ipaddress, self.portaddress)
        self.socket.bind(self.server_address)
        self.socket.setblocking(1)
        self.socket.listen(10)
        print('Starting up on {} port {}'.format(*self.server_address))
        self._wait_for_new_connections()

    def _wait_for_new_connections(self):
        while True:
            connection, _ = self.socket.accept()
            _thread.start_new_thread(self._on_new_client, (connection,))

    def _on_new_client(self, connection):
        global f
        try:
            # Declare the client's name
            client_name = f.decrypt(connection.recv(1024)).decode("utf-8").upper()
            self.users_table[connection] = client_name
            print(f'{client_name} joined the redroom.')
            for conn in self.users_table:
                    data = f'{client_name} joined the redroom.'
                    encrypted_mes = f.encrypt(str.encode(data))
                    conn.sendall(encrypted_mes) 
            while True:
                self.multicast((connection.recv(1024)), owner=connection) 
        except:
            print(f'{client_name} left the room.')
            for conn in self.users_table:
                data = f'{client_name} left the redroom.'
                encrypted_mes = f.encrypt(str.encode(data))
                conn.sendall(encrypted_mes) 
            self.users_table.pop(connection)
            connection.close()

    def multicast(self, message, owner=None):
        for conn in self.users_table:
            if conn==owner:
                continue
            conn.sendall(message)

if __name__ == "__main__":
    ip = sys.argv[1]
    port = sys.argv[2]
    Server(ip, int(port))