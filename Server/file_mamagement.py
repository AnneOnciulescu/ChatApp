from datetime import date
from key_gen import Key
from time import sleep

class File:
    def __init__(self):
        self.end_str = '\n###END###\n'
        self.bound_str = '\n###\n'
        self.keys = Key()

    def send_today_messages(self,client_socket, public_key):
        self.title = date.today()

        try:
            f = open(f"./Messages/{str(self.title)}.txt", "rt")
            messages = f.read()
            messages_list = [item.strip() for item in messages.split(self.bound_str) if item.strip()]
            # print(messages_list)

            for message in messages_list:
                message_encr = self.keys.encrypt(message + self.bound_str, public_key)
                message_encr += self.end_str

                client_socket.sendall(message_encr.encode('utf-8'))
                sleep(20e-3)
                
            
        except:
            f = open(f"./Messages/{str(self.title)}.txt", "x")
            message = "None"
            message_encr = self.keys.encrypt(message, public_key)
            message_encr += self.end_str

            client_socket.sendall(message_encr.encode('utf-8'))
        
        finally:
            f.close()

    def write_message(self, data):
        self.title = date.today()
        f = open(f"./Messages/{str(self.title)}.txt", "at")

        f.write(data)
        f.write(self.bound_str)
        f.close()


    def check_for_user(self, user_data):
        f = open('./Users/users.txt', 'r')

        for line in f:
            if line[:-1] == user_data:
                f.close()
                return True
            
        f.close()
        return False
    
    def create_request(self, user_data):
        f = open('./Users/requests.txt', 'at')

        f.writelines([user_data + '\n'])
        f.close()

        print('new user')