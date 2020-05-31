import time
import json
from json import JSONEncoder

class Channel:
    def __init__(self, name, private=False):
        self.name = name
        self.private = private
        self.messages = []

    def get_json(self):
        return json.dumps(
            {
                "name": self.name,
                "messages": self.messages
            })

    def add_message(self, user, content):
        message = {
            "user": user,
            "content": content,
            "timestamp": time.time()
        }
        self.messages.append(message)
        
        # Make sure we have at most 100 messages
        while len(self.messages) > 100:
            self.messages.pop(0)

class PrivateChannel(Channel):
    def __init__(self, name, users):
        super().__init__(name, private=True)
        self.users = users
    
    # Make sure the user is allowed to send to this channel
    def add_message(self, user, content):
        if user in self.users:
            super().add_message(user, content)

    def get_json(self):
        return json.dumps(
            {
                "name": self.name,
                "messages": self.messages,
                "users": self.users
            })