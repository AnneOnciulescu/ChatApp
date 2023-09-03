from datetime import date

class File:
    def __init__(self):
        self.end_str = '\n###END###\n'
        self.bound_str = '\n###\n'

    def send_today_messages(self, client_socket):
        self.title = date.today()

        try:
            f = open(f"./Messages/{str(self.title)}.txt", "rt")

            messages = f.read()
            messages += self.end_str

            client_socket.sendall(messages.encode('utf-8'))
            
        except:
            f = open(f"./Messages/{str(self.title)}.txt", "x")
            client_socket.sendall(("None" + self.end_str).encode('utf-8'))
        
        finally:
            f.close()

    def write_message(self, data):
        f = open(f"./Messages/{str(self.title)}.txt", "a")

        f.write(data[:-len(self.end_str)])
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
        f = open('./Users/requests.txt', 'a')

        f.writelines([user_data + '\n'])
        f.close()

        print('new user')
        raise ValueError('User does not have access yet')