import socket
import select
from file_mamagement import File
from key_gen import Key
import uuid

class Server:
    def __init__(self):
        HOST = "0.0.0.0"
        PORT = 9000

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.server.bind((HOST, PORT))
        self.server.listen(5)

        self.socket_pool = [self.server]

        self.file_mamagement = File()
        self.keys = Key()

    def recv_all(self, socket):
        buff = ''

        while True:
            data = socket.recv(1024).decode('utf-8')

            if not data:
                print('connection closed')
                break

            buff += data
            if buff.endswith(self.file_mamagement.end_str):
                return buff



    def start(self):
        while True:
            readable, _, _ = select.select(self.socket_pool, [], [])

            for sock in readable:
                if sock == self.server:

                    client_socket, client_address = self.server.accept()
                    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    client_socket.settimeout(1)

                    print(f"Accepted connection from {client_address}")

                    try:
                        client_public_key = self.recv_all(client_socket)[:-len(self.file_mamagement.end_str)]
                        self.keys.validate_key(client_public_key.encode('utf-8'))
                        print(client_public_key)

                        server_public_key = self.keys.public_pem.decode('utf-8') + self.file_mamagement.end_str
                        client_socket.sendall(server_public_key.encode('utf-8'))
                        print(server_public_key)


                        client_encr_data = self.recv_all(client_socket)[:-len(self.file_mamagement.end_str)]
                        client_data = self.keys.decrypt(client_encr_data)

                        print(client_data)
                        if not self.file_mamagement.check_for_user(client_data):
                            self.file_mamagement.create_request(client_data)

                        self.file_mamagement.send_today_messages(client_socket)

                        self.socket_pool.append(client_socket)
                    except:
                        print('Tea pot detected =)))))))')
                        client_socket.sendall("you're a tea pot =)".encode('utf-8'))
                        client_socket.close()

                else:
                    data = self.recv_all(sock)
                    
                    if data:
                        # Handle the received data
                        print(f"Received data: {data}")
                        self.file_mamagement.write_message(data)
                        
                        for client in self.socket_pool[1:]:
                            client.sendall(data.encode('utf-8'))
                    else:
                        # No data received, the client has closed the connection
                        print(f"Connection from {sock.getpeername()} closed")
                        sock.close()
                        self.socket_pool.remove(sock)
