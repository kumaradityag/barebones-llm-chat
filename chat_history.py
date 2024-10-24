from dataclasses import dataclass
import dataclasses
from enum import Enum
from typing import List, Tuple, Union


# class syntax

class CHAT_ROLE(Enum):
    SYSTEM = 1
    USER = 2
    ASSISTANT = 3

@dataclass
class ChatHistory:
    history: Tuple = tuple()
    images: Tuple = tuple()

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

    def add(self, role: Union[CHAT_ROLE, str], message):
        if isinstance(role, CHAT_ROLE):
            role = role.name

        new_history = (*self.history, {"role": role, "content": message})
        return self.replace(history=new_history)

    def add_img(self, image):
        return self.replace(images=(*self.images, image))

    def pack(self) -> str:
        ret = []
        for message in self.history:
            ret.append(f"{message['role'].capitalize()}: {message['content']}")
        
        ret = "\n".join(ret) + " Assistant:"
        return ret
    
    def pretty(self):
        ret = []
        for message in self.history:
            ret.append(f"{message['role'].capitalize()}: {message['content']}")

        return "\n\n".join(ret)

if __name__ == "__name__":
    ch = ChatHistory()
