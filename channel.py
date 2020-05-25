import time
import json
from json import JSONEncoder

class Channel:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.add_message("FlackBot", "Welcome to your brand new channel!")

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
