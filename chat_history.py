from enum import Enum
from typing import Union


# class syntax

class CHAT_ROLE(Enum):
    SYSTEM = 1
    USER = 2
    ASSISTANT = 3

class ChatHistory:
    def __init__(self):
        self.history = []

    def append(self, role: Union[CHAT_ROLE, str], message):
        self.history.append({"role": role, "content": message})

    @property
    def get(self):
        return self.history