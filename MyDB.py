import socket
import threading
from datetime import datetime
import json
from key_gen import Key

class DBConnection:
    def __init__(self):
        self.message_send = ''
        self.message_recv = ''

        self.end_str = '\n###END###\n'
        self.bound_str = '\n###\n'

        self.messages = []

        self.condition_send = threading.Condition()
        self.keys = Key()

        self.HOST = '82.210.153.205'
        self.PORT = 9000

    def login(self, username, password_code):
        self.username = username
        self.password_code = password_code

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.HOST, self.PORT))

        public_key_format = self.keys.public_pem.decode('utf-8') + self.end_str
        print(public_key_format)
        self.socket.sendall(public_key_format.encode('utf-8'))

        self.server_public_key = self.recv_all()[:-len(self.end_str)]
        print(self.server_public_key)

        encr_user_data = self.keys.encrypt(f"{self.username}: {password_code}", self.server_public_key) + self.end_str
        self.socket.sendall(encr_user_data.encode('utf-8'))

        status_encr = self.recv_all()[:-len(self.end_str)]
        status = self.keys.decrypt(status_encr)
        print(status)

        if status != 'OK':
            self.socket.close()
            return False

        return True
        

    def start_messages(self):
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

            message_encr = self.keys.encrypt(self.message_send, self.server_public_key)
            message_encr += self.end_str

            self.socket.sendall(message_encr.encode('utf-8'))

            print(f"Send: {self.message_send}")
            self.message_send = ''


    def recv_all(self):
        buff = ''

        while True:
            data = self.socket.recv(1024).decode('utf-8')

            if not data:
                break

            buff += data
            if buff.endswith(self.end_str):
                return buff

    def recv_message(self):
        while True:
            self.message_recv = self.recv_all()
            if not self.message_recv:
                print('connection closed')
                break
            
            self.message_recv = self.message_recv[:-len(self.end_str)]
            message_dec = self.keys.decrypt(self.message_recv)
            print(message_dec)

            if message_dec != 'None':
                messages_list = [item.strip() for item in message_dec.split(self.bound_str) if item.strip()]

                for message in messages_list:
                    self.messages.append(message)
            print(f"Received: {messages_list}")


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

