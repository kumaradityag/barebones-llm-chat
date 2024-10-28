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

    def get_all_image_hashes(self):
        images = [chat["image"] for chat in self.history if chat["image"] is not None]
        return images

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

    def add(self, role: Union[CHAT_ROLE, str], message, image=None):
        if isinstance(role, CHAT_ROLE):
            role = role.name

        new_message = {"role": role, "content": message, "image": image}
        new_history = (*self.history, new_message)
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
