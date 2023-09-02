import socket
import threading
from datetime import datetime
import json

class DBConnection:
    def __init__(self, username):
        self.username = username
        self.message_send = ''
        self.message_recv = ''

        self.messages = []

        self.condition_send = threading.Condition()

        HOST = '82.210.153.205'
        PORT = 8080

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        send_thread = threading.Thread(target=self.send_message)
        recv_thread = threading.Thread(target=self.recv_message)

        send_thread.daemon = True
        recv_thread.daemon = True

        # Start the threads
        recv_thread.start()
        send_thread.start()

    def send_message(self):
        while True:
            with self.condition_send:
                if not self.message_send:
                    self.condition_send.wait()

            self.socket.sendall(self.message_send.encode('utf-8'))
            print(f"Send: {self.message_send}")
            self.message_send = ''


    def recv_message(self):
        while True:
            self.message_recv = self.socket.recv(1024)
            if not self.message_recv:
                break

            if self.message_recv != 'None':
                messages_list = [item.strip() for item in self.message_recv.decode('utf-8').split('\n####\n') if item.strip()]

                for message in messages_list:
                    self.messages.append(message)
            print(f"Received: {self.message_recv}")


    def get_new_messages(self):
        new_messages = []
        for message in self.messages:
            new_messages.append(json.loads(message))

        self.messages = []
        return new_messages
    
    def get_recent_messages(self):
        pass

    def create_message(self, message):
        now = datetime.now()

        new_message = {
            'user': self.username,
            'message': message,
            'timestamp': str(now)
        }

        self.message_send = json.dumps(new_message)
        with self.condition_send:
            self.condition_send.notify()

