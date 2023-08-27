from pymongo import MongoClient
from datetime import datetime


class DBConnection:
    def __init__(self, connectionStr, username):
        self.username = username

        client = MongoClient(connectionStr)
        self.mongo_db = client['ChatApp']
        self.messages = self.mongo_db[username]
        print("Connection Successful")

    def send_message(self, message):
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        new_message = {
            'user': self.username,
            'message': message,
            'timestamp': now
        }

        self.messages.insert_one(new_message)
        print("OK")

    def delete_message(self, message, timestamp):
        self.messages.delete_one({"message": message, "timestamp": timestamp})
        print("OK")

    def get_messages_in_order(self):
        message_list = []

        for username in self.mongo_db.list_collection_names():
            for message in self.mongo_db[username].find({}):
                message_list.append(message)

        message_list.sort(key=lambda x : x['timestamp'])

        return message_list