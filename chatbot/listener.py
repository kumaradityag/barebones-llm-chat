import time
import websocket
import json
import threading

WS_URL = "ws://127.0.0.1:5000"  # Replace with your server's WebSocket address

# Buffer to store incoming messages for batching
message_buffer = []
batch_interval = 5  # N seconds for batching


# Function to process and answer batched messages
def process_batch():
    while True:
        time.sleep(batch_interval)
        if message_buffer:
            # Fetch images if needed and send responses here
            messages = message_buffer[:]
            message_buffer.clear()
            print(f"Processing batch of {len(messages)} messages")
            # Call LLM to respond to messages...


def on_message(ws, message):
    data = json.loads(message)
    chat_id = data.get("chat_id")
    message = data.get("message")

    # Add new message to the buffer
    message_buffer.append({'chat_id': chat_id, 'message': message})

    # Example: Check if image is needed (using hash) and fetch if missing
    if 'image' in message:
        image_hash = message['image']
        # Check local cache or fetch from server if not found


def on_error(ws, error):
    print(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")


def on_open(ws):
    print("Connected to WebSocket")


def start_websocket():
    ws = websocket.WebSocketApp(WS_URL,
                                #on_open=on_open,
                                #on_message=on_message,
                                #on_error=on_error,
                                #on_close=on_close
                                )
    ws.run_forever()


# Start WebSocket in a separate thread
ws_thread = threading.Thread(target=start_websocket)
ws_thread.start()

# Start the message processing batch loop
process_batch()