from time import sleep

import requests
import json

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from barebonesllmchat.common.chat_history import CHAT_ROLE, ChatHistory, ChatHistoryWithImages

class ChatbotClient:
    def __init__(self, base_url, api_key, use_websocket=True):
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

    def send_message(self, chat_id, content, role="USER", image_path=None, blocking=True):
        chat_id = chat_id

        data = {
            "chat_id": chat_id,
            "api_key": self.api_key,
            "role": role,
            "message": content
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

    def send_history(self, chat_id, chat_history_with_images, blocking=True):
        data = {
            "chat_id": chat_id,
            "api_key": self.api_key,
            "chat_history": json.dumps(chat_history_with_images.chat_history.history),
        }

        self.chat_readiness[chat_id] = False
        response = requests.post(f"{self.base_url}/send_history", data=data, files=chat_history_with_images.open_images())
        response.raise_for_status()

        if blocking:
            assert self.use_websocket
            self.wait_for_chat_ready(chat_id)

    def wait_for_chat_ready(self, chat_id):
        while True:
            if self.chat_readiness[chat_id] == False:
                sleep(0.1)
            else:
                break

# Usage example
if __name__ == "__main__":
    client = ChatbotClient("http://127.0.0.1:5000", "your_api_key")
    chat_id = client.create_chat()
    client.send_message(chat_id, "Hello from the Python client!", blocking=False)
    client.wait_for_chat_ready(chat_id)

    client.send_message(chat_id, "Very cool!")
    client.wait_for_chat_ready(chat_id)

    print(client.get_chat_messages(chat_id).pretty())
    print()
    print()

    chat_history_with_images = ChatHistoryWithImages(client.get_chat_messages(chat_id), {})
    chat_history_with_images = chat_history_with_images.add(CHAT_ROLE.USER, "Can you describe this image?", "/home/charlie/Downloads/block-tower.jpg")

    client.send_history("new chat!", chat_history_with_images)

    print(client.get_chat_messages("new chat!").pretty())
