import threading

from pymongo import MongoClient
from datetime import datetime, timedelta


class DBConnection:
    def __init__(self, connection_str, username):
        self.username = username
        self.time = datetime.now()

        self.messages_list = []
        self.thread_list = []

        client = MongoClient(connection_str)
        self.mongo_db = client['ChatApp']
        self.messages = self.mongo_db[username]
        print("Connection Successful")

    def detect_changes(self):
        for username in self.mongo_db.list_collection_names():
            t = threading.Thread(target=self.detect_change, args=[self.mongo_db[username]])
            t.daemon = True
            self.thread_list.append(t)
            t.start()

    def detect_change(self, collection):
        with collection.watch() as stream:
            for change in stream:
                # print("Change detected:", change)
                self.messages_list.append(change['fullDocument'])

    def send_message(self, message):
        now = datetime.now()
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

    def get_new_messages(self):
        messages = self.messages_list
        self.messages_list = []

        return messages

    def get_recent_messages(self):
        msg_list = []
        query = {"timestamp": {"$gt": self.time - timedelta(hours=24)}}

        for username in self.mongo_db.list_collection_names():
            for message in self.mongo_db[username].find(query):
                msg_list.append(message)

        msg_list.sort(key=lambda x: x['timestamp'])

        return msg_list
