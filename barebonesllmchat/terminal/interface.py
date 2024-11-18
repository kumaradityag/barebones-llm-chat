import time
from datetime import datetime
from time import sleep
from typing import Union

import requests
import json

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from barebonesllmchat.common.chat_history import CHAT_ROLE, ChatHistory, ChatHistoryWithImages

class ChatbotClient:
    def __init__(self, base_url, api_key, use_websocket=True, send_history_base_chatname="new chat!", send_history_increment_chatname=True):
        self.base_url = base_url
        self.api_key = api_key

        self.chat_readiness = {}

        self.use_websocket = use_websocket
        if self.use_websocket:

            import socketio
            sio = socketio.Client()
            @sio.on('new_message_from_assistant')
            def on_message(data):
                chat_id = data.get("chat_id")

                chat_history = self.get_chat_messages(chat_id)
                self.chat_readiness[chat_id] = chat_history

            sio.connect(f"{self.base_url}")
            self.sio = sio

        self.send_history_base_chatname = send_history_base_chatname
        self.send_history_increment_chatname = send_history_increment_chatname
        self.send_history_index = 0


    def set_api_key(self, api_key):
        self.api_key = api_key

    def get_chats(self):
        response = requests.get(f"{self.base_url}/get_chats")
        response.raise_for_status()
        chats = response.json()
        return chats

    def create_chat(self):
        response = requests.post(
            f"{self.base_url}/create_chat",
            data={"api_key": self.api_key}
        )
        response.raise_for_status()
        chat_data = response.json()
        return chat_data.get("chat_id")

    def delete_chat(self, chat_id):
        response = requests.post(
            f"{self.base_url}/delete_chat/{chat_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            data={"api_key": self.api_key}
        )
        response.raise_for_status()

    def get_chat_messages(self, chat_id):
        response = requests.get(f"{self.base_url}/get_chat/{chat_id}")
        response.raise_for_status()
        return ChatHistory(tuple(response.json()))

    def send_message(self, chat_id: Union[None, str], content, generation_settings={}, role="USER", image_path=None, blocking=True) -> str:
        if chat_id is None or chat_id not in list(self.get_chats()):
            chat_id = self.send_history(chat_id, ChatHistory(), blocking=True)  # creates a chat with the resolved name

        data = {
            "chat_id": chat_id,
            "api_key": self.api_key,
            "role": role,
            "message": content,
            "generation_settings": json.dumps(generation_settings),
        }

        files = {}
        if image_path:
            files['image'] = open(image_path, 'rb')

        self.chat_readiness[chat_id] = False
        response = requests.post(f"{self.base_url}/send_message", data=data, files=files)
        response.raise_for_status()

        if blocking:
            assert self.use_websocket
            self.wait_for_chat_ready(chat_id)

        return chat_id

    def _resolve_phantom_chat_name(self):
        def gen():
            if self.send_history_increment_chatname:
                tentative_chat_name = f"{self.send_history_base_chatname} ({self.send_history_index})"
                self.send_history_index += 1
            else:
                tentative_chat_name = f"{self.send_history_base_chatname}"
            return tentative_chat_name

        tentative_chat_name = gen()

        chats = self.get_chats()
        if tentative_chat_name not in chats:
            return tentative_chat_name

        # tentative chat name is in chats
        prefix = self.send_history_base_chatname

        chats = list(filter(lambda x: prefix in x, chats))
        maxindex = max(list(map(lambda x: int(x.split(f"{prefix} (")[1].split(")")[0]), chats)))
        self.send_history_index = maxindex + 1

        return gen()


    def send_history(self, chat_id: Union[None, str], chat_history_maybe_with_images: Union[ChatHistoryWithImages, ChatHistory], generation_settings={}, blocking=True):
        if chat_id is None:
            chat_id = self._resolve_phantom_chat_name()

        if isinstance(chat_history_maybe_with_images, ChatHistoryWithImages):
            chat_history_data = chat_history_maybe_with_images.chat_history.history
        else:
            chat_history_data = chat_history_maybe_with_images.history

        image_files = None
        if isinstance(chat_history_maybe_with_images, ChatHistoryWithImages):
            image_files = chat_history_maybe_with_images.open_images()

        data = {
            "chat_id": chat_id,
            "api_key": self.api_key,
            "chat_history": json.dumps(chat_history_data),
            "generation_settings": json.dumps(generation_settings)
        }

        self.chat_readiness[chat_id] = False
        response = requests.post(f"{self.base_url}/send_history", data=data, files=image_files)
        response.raise_for_status()

        if blocking:
            assert self.use_websocket
            self.wait_for_chat_ready(chat_id)

        return chat_id

    def wait_for_chat_ready(self, chat_id, max_timeout=None):
        # is this the right approach? no
        # do i love wasting CPU cycles? SO MUCH

        start_time = datetime.now()

        while True:
            if self.chat_readiness[chat_id] == False:
                sleep(0.1)
            else:
                break

            if max_timeout is None:
                continue

            if (datetime.now() - start_time).total_seconds() >= max_timeout:
                raise TimeoutError

# Usage example
if __name__ == "__main__":
    client = ChatbotClient("http://127.0.0.1:5000", "your_api_key")

    chat_id = client.send_history(None,
                                  ChatHistory().add(CHAT_ROLE.USER, "Bonjour baguette!"),
                                  generation_settings={"max_new_tokens": 512, "temperature": 0.0}
                                  )  # chat_history_with_images)

    print(chat_id)
    print(client.get_chat_messages(chat_id).pretty())
    exit()


    chat_id = client.send_message(
        None,
        "Ignore any images. Please tell me how to go from point A to point B.",
        generation_settings={"max_new_tokens": 100, "temperature": 0.0},
        blocking=True)

    print(client.get_chat_messages(chat_id).pretty())
    exit()



    chat_id = client.create_chat()
    client.send_message(chat_id, "Hello from the Python client!", blocking=False)
    client.wait_for_chat_ready(chat_id)

    client.send_message(chat_id, "Very cool!")
    client.wait_for_chat_ready(chat_id)

    print(client.get_chat_messages(chat_id).pretty())
    print()
    print()

    #chat_history_with_images = ChatHistoryWithImages(client.get_chat_messages(chat_id), {})
    #chat_history_with_images = chat_history_with_images.add(CHAT_ROLE.USER, "Can you describe this image?", "/home/charlie/Downloads/block-tower.jpg")

    client.send_history("new chat!", client.get_chat_messages(chat_id))# chat_history_with_images)

    print(client.get_chat_messages("new chat!").pretty())
