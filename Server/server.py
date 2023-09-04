import socket
import select
from file_mamagement import File
from key_gen import Key

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

        self.socket_key = []

    def recv_all(self, socket):
        buff = ''

        while True:
            data = socket.recv(1024)

            if not data:
                print('connection closed')
                break

            data = data.decode('utf-8')
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
                    client_socket.settimeout(2)

                    print(f"Accepted connection from {client_address}")

                    try:
                        client_public_key = self.recv_all(client_socket)[:-len(self.file_mamagement.end_str)]
                        self.keys.validate_key(client_public_key.encode('utf-8'))
                        print(client_public_key)

                        server_public_key = self.keys.public_pem.decode('utf-8') + self.file_mamagement.end_str
                        client_socket.sendall(server_public_key.encode('utf-8'))
                        print(server_public_key)

                        # sleep(200e-3)
                        client_encr_data = self.recv_all(client_socket)[:-len(self.file_mamagement.end_str)]
                        client_data = self.keys.decrypt(client_encr_data)

                        print(client_data)
                        if self.file_mamagement.check_for_user(client_data):
                            client_socket.settimeout(None)
                            
                            status = self.keys.encrypt("OK", client_public_key)
                            self.socket_key.append({'socket': client_socket, 'key': client_public_key})

                            status += self.file_mamagement.end_str
                            client_socket.sendall(status.encode('utf-8'))

                            self.file_mamagement.send_today_messages(client_socket, client_public_key)
                            self.socket_pool.append(client_socket)

                        else:
                            self.file_mamagement.create_request(client_data)
                            status = self.keys.encrypt("New User", client_public_key)
                            status += self.file_mamagement.end_str
                            client_socket.sendall(status.encode('utf-8'))
                            print('connection closed')
                            client_socket.close()
                    except:
                        print('ciupalezuuuuu')
                        client_socket.close()


                else:
                    data = self.recv_all(sock)
                    
                    if data:
                        data_decr = self.keys.decrypt(data[:-len(self.file_mamagement.end_str)])
                        # Handle the received data
                        print(f"Received data: {data_decr}")
                        self.file_mamagement.write_message(data_decr)
                        

                        for d in self.socket_key:
                            if d['socket'] != self.server:

                                key = d['key']
                                client = d['socket']
                                data_encr = self.keys.encrypt(data_decr, key)
                                data_encr += self.file_mamagement.end_str

                                client.sendall(data_encr.encode('utf-8'))

                    else:
                        sock.close()
                        self.socket_pool.remove(sock)
                        for d in self.socket_key:
                            if d['socket'] == sock:
                                self.socket_key.remove(d)
                                break