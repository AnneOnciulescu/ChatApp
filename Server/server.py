import socket
import select
from datetime import date


def recv_all(socket):
    buff = ''

    while True:
        data = socket.recv(1024).decode('utf-8')

        if not data:
            break

        buff += data
        if buff.endswith(end_str):
            return buff


HOST = "0.0.0.0"
PORT = 8080
end_str = '\n###END###\n'
bound_str = '\n###\n'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

server.bind((HOST, PORT))

server.listen(5)
socket_pool = [server]

while True:
    readable, _, _ = select.select(socket_pool, [], [])

    for sock in readable:
        if sock == server:

            print("ceva")
            client_socket, client_address = server.accept()
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            print(f"Accepted connection from {client_address}")
            socket_pool.append(client_socket)

            title = date.today()

            try:
                f = open(f"./Messages/{str(title)}.txt", "rt")
                # print(f.read())
                messages = f.read()
                messages += end_str

                client_socket.sendall(messages.encode('utf-8'))
                f.close()
            except:
                f = open(f"./Messages/{str(title)}.txt", "x")
                client_socket.sendall("None" + end_str)
                f.close()

        else:
            data = recv_all(sock)
            
            if data:
                # Handle the received data
                print(f"Received data: {data}")
                f = open(f"./Messages/{str(title)}.txt", "a")
                f.write(data[:-len(end_str)])
                f.write(bound_str)
                f.close()
                for client in socket_pool[1:]:
                    client.sendall(data.encode('utf-8'))
            else:
                # No data received, the client has closed the connection
                print(f"Connection from {sock.getpeername()} closed")
                sock.close()
                socket_pool.remove(sock)
