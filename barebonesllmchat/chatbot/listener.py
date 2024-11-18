import json
import os
import pathlib
import shutil
import sys
import traceback
import requests
try:
    import socketio
except Exception:
    print("Could not import socketio. Are you sure it's installed? Are you sure you activated your venv/conda?", file=sys.stderr)
    traceback.format_exc()
    exit(1)
from PIL import Image

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from barebonesllmchat.common.chat_history import ChatHistory

secrets = json.load(open(pathlib.Path(__file__).parent.parent / "secrets" / 'secrets.json'))
CONST_SERVER_IP = secrets["server_ip"]
api_key = secrets["valid_api_keys"][0]

try:
    sio = socketio.Client()
    sio.connect(f'http://{CONST_SERVER_IP}:{secrets["server_port"]}')
except Exception as e:
    print("Could not connect to the API. Is it running? Are you sure you opened or tunnel'd a port?", file=sys.stderr)
    raise e

CONST_DOWNLOADS_TO_KEEP = 10
CONST_DOWNLOAD_DIR = secrets["listener_download_dir"]   #"./downloads"
shutil.rmtree(CONST_DOWNLOAD_DIR, ignore_errors=True)   # todo maybe not wipe downloads every init
os.makedirs(CONST_DOWNLOAD_DIR, exist_ok=True)

from barebonesllmchat.chatbot.molmo_bot import Olmo
LLM = Olmo()

@sio.on('new_message_from_user')
def message_event(data):
    # gets called whe
    print("I received")
    print(data)

    #data = json.loads(data)
    chat_id = data['chat_id']
    chat = ChatHistory(tuple(json.loads(data["chat_history"])))

    traverse_and_download_images(chat)
    images = traverse_and_get_images(chat)

    if len(images) == 0:
        images = None

    new_chat = LLM.respond(chat, images)

    send_message(chat_id, "assistant", new_chat.history[-1]["content"], "your_api_key")


def send_message(chat_id, role, message, api_key):
    """Send a response message to the user via the home server, with optional image."""
    # Prepare the form data
    form_data = {
        "chat_id": chat_id,
        "api_key": api_key,
        "role": role,
        "message": message,
    }

    # Prepare the image data if an image is provided

    response = requests.post(
        f"http://{CONST_SERVER_IP}:{secrets['server_port']}/send_message",
        data=form_data,
        files=None
    )
    if response.status_code == 200:
        print(f"Message sent to chat {chat_id}")
    else:
        print(f"Failed to send message to chat {chat_id}: {response.status_code}")

# todo only keep N local images if needed idk
"""
def scrub_downloads():
    list_of_files = os.listdir(CONST_DOWNLOAD_DIR)
    paths = [f"{CONST_DOWNLOAD_DIR}/{x}" for x in list_of_files]

    if len(paths) < 10:
        return

    #times = np.array(list(map(os.path.getctime, paths)))



    #if len(list_of_files) == 25:
    #    oldest_file = min(full_path, key=os.path.getctime)
    #    os.remove(oldest_file)
"""

def traverse_and_download_images(chat_history):
    images = chat_history.get_all_image_hashes()

    def download_image_if_missing(image_hash):
        """Downloads image from the server if it's missing locally."""
        image_path = os.path.join(CONST_DOWNLOAD_DIR, f"{image_hash}")

        if not os.path.exists(image_path):
            print(f"Image {image_hash} not found locally. Downloading...")
            response = requests.get(f"http://{CONST_SERVER_IP}:{secrets['server_port']}/get_image/{image_hash}")

            if response.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(response.content)
                print(f"Image {image_hash} downloaded and saved.")
            else:
                print(f"Failed to download image {image_hash}: {response.status_code}")
        else:
            print(f"Image {image_hash} already exists locally.")

    for image in images:
        download_image_if_missing(image)

def traverse_and_get_images(chat_history):
    images = chat_history.get_all_image_hashes()

    images = [Image.open(f"{CONST_DOWNLOAD_DIR}/{image}") for image in images]
    return images


if __name__ == '__main__':
    sio.wait()

