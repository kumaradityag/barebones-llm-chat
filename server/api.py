import atexit
import functools
import json
import os
import hashlib
import shutil
import signal

from flask import Flask, request, jsonify, send_from_directory
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
import dataclasses
from typing import Dict, Tuple, Union

from server.random_names import generate_name

# Initialize Flask app
app = Flask(__name__)

# Configure the image storage directory
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Class and chat history definitions (reuse your existing classes)

class CHAT_ROLE(Enum):
    SYSTEM = 1
    USER = 2
    ASSISTANT = 3


@dataclass
class ChatHistory:
    history: Tuple = tuple()

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

    def add(self, role: Union[CHAT_ROLE, str], message, image=None):
        if isinstance(role, CHAT_ROLE):
            role = role.name

        new_message = {"role": role, "content": message, "image": image}
        new_history = (*self.history, new_message)
        return self.replace(history=new_history)

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


# In-memory store for chat histories
chats: Dict[str, ChatHistory] = {}

def chat_names():
    return list(chats.keys())


CONST_CHAT_SAVE_PATH = "./saved_chat.json"

def graceful_bootup():
    global chats
    if os.path.exists(CONST_CHAT_SAVE_PATH):
        with open(CONST_CHAT_SAVE_PATH, "r") as jsonfile:
            temp_chats = json.load(jsonfile)

        temp_chats = {chat_name: ChatHistory(tuple(history)) for chat_name, history in temp_chats.items()}
        chats = temp_chats
graceful_bootup()

def graceful_shutdown(signum, frame):
    global chats
    temp_chats = {chat_name: chat.history for chat_name, chat in chats.items()}
    with open(CONST_CHAT_SAVE_PATH, "w") as jsonfile:
        jsonned = json.dumps(temp_chats)
        jsonfile.write(jsonned)
    exit()

# Register the graceful shutdown function for SIGTERM and SIGINT
signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)

# Also ensure cleanup happens when the process exits
#atexit.register(functools.partial(graceful_shutdown, None, None))

# API key authentication (simple check for now)
API_KEY = "your_api_key"


def authenticate(api_key):
    return api_key == API_KEY


# Helper function to hash image content
def hash_image(image_content):
    return hashlib.sha256(image_content).hexdigest()


# Save image to the server and return its hash
def save_image(image_file):
    image_content = image_file.read()
    image_hash = hash_image(image_content)
    image_path = os.path.join(UPLOAD_FOLDER, image_hash)

    if not os.path.exists(image_path):
        # Save the image if it doesn't exist yet
        with open(image_path, 'wb') as f:
            f.write(image_content)

    return image_hash


# Create a new chat
@app.route('/create_chat', methods=['POST'])
def create_chat():
    chat_id = generate_name(chat_names())
    #chat_id = str(uuid4())
    chats[chat_id] = ChatHistory()
    return jsonify({"chat_id": chat_id}), 201


# Get all chat IDs
@app.route('/get_chats', methods=['GET'])
def get_chats():
    return jsonify(list(chats.keys()))


# Send a message to a chat, including image handling
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.form.to_dict()
    chat_id = data.get('chat_id')
    api_key = data.get('api_key')
    role = data.get('role')
    message = data.get('message')
    image = request.files.get('image')

    if not authenticate(api_key):
        return jsonify({"error": "Unauthorized"}), 403

    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404

    image_hash = None
    if image:
        # Save the image and get its hash
        image_hash = save_image(image)

    # Add the message (with image hash if applicable)
    chats[chat_id] = chats[chat_id].add(role, message, image=image_hash)
    return jsonify({"status": "Message added"}), 200


# Get the history of a specific chat (returns image hashes)
@app.route('/get_chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404

    return jsonify(chats[chat_id].history)


# Delete a specific chat
@app.route('/delete_chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404

    def get_images_for_chat(key):
        cur_chat = chats[key].history
        images = [chat["image"] for chat in cur_chat if chat["image"] is not None]
        return images

    images_of_all_chats = {key: get_images_for_chat(key) for key in chats}

    unsafe_images = []
    chat_id_images = images_of_all_chats[chat_id]
    for image in chat_id_images:
        for key, other_chat_images in images_of_all_chats.items():
            if key == chat_id:
                continue
            if image in other_chat_images:
                unsafe_images.append(image)

    safe_images = set(images_of_all_chats[chat_id]) - set(unsafe_images)

    for safe_image in safe_images:
        os.remove(os.path.join(UPLOAD_FOLDER, safe_image))

    del chats[chat_id]
    return jsonify({"status": "Chat deleted"}), 200


# Get chats where the latest message is from the user (for the cluster)
@app.route('/get_new_messages', methods=['GET'])
def get_new_messages():
    user_chats = {chat_id: chat.history for chat_id, chat in chats.items()
                  if chat.history and chat.history[-1]["role"] == "USER"}

    return jsonify(user_chats)


# Retrieve an image by its hash
@app.route('/get_image/<image_hash>', methods=['GET'])
def get_image(image_hash):
    image_path = os.path.join(UPLOAD_FOLDER, image_hash)
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404

    return send_from_directory(UPLOAD_FOLDER, image_hash)

@app.route('/')
def serve_homepage():
    return send_from_directory('static', 'index.html')


# Run the Flask app
if __name__ == '__main__':

    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        # This except block will handle a keyboard interrupt (Ctrl+C)
        graceful_shutdown()

