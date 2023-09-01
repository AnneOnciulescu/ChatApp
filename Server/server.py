import socket
import select
from datetime import date

HOST = "0.0.0.0"
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

server.bind((HOST, PORT))


server.listen(5)
socket_pool = [server]

while True:
    readable, _, _ = select.select(socket_pool, [], [])

    for sock in readable:
        if sock == server:

            client_socket, client_address = server.accept()
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            print(f"Accepted connection from {client_address}")
            socket_pool.append(client_socket)

            title = date.today()

            try:
                f = open(f"./Messages/{str(title)}.txt", "rt")
                # print(f.read())
                messages = f.read()
                client_socket.sendall(messages.encode('utf-8'))
                f.close()
            except:
                f = open(f"./Messages/{str(title)}.txt", "x")
                client_socket.sendall("None")
                f.close()

        else:
            data = sock.recv(1024)
            
            if data:
                # Handle the received data
                print(f"Received data: {data.decode('utf-8')}")
                f = open(f"./Messages/{str(title)}.txt", "a")
                f.write(data.decode('utf-8'))
                f.write('\n####\n')
                f.close()
                for client in socket_pool[1:]:
                    client.sendall(data)
            else:
                # No data received, the client has closed the connection
                print(f"Connection from {sock.getpeername()} closed")
                sock.close()
                socket_pool.remove(sock)
