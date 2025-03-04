import time

from barebonesllmchat.common.chat_history import ChatHistory, CHAT_ROLE
from barebonesllmchat.terminal.interface import ChatbotClient

client: ChatbotClient = None

def set_client():
    global client
    client = ChatbotClient("http://127.0.0.1:5000", "your_api_key")

def maybe_set_client():
    global client
    if client is None:
        set_client()

class TryAgain(Exception):
    pass

class ChatCompletion:
    @classmethod
    def create(cls, *args, **kwargs):
        """
                Creates a new chat completion for the provided messages and parameters.

                See https://platform.openai.com/docs/api-reference/chat-completions/create
                for a list of valid parameters.
                """
        maybe_set_client()

        start = time.time()
        timeout = kwargs.pop("timeout", None)

        while True:
            try:
                return cls._chat_complete(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

    @classmethod
    def _chat_complete(self, *args, **kwargs):
        assert len(args) == 0 or len(args) == 1

        if len(args) == 1:
            msg = args[0]
        else:
            try:
                msg = kwargs["prompt"]
                del kwargs["prompt"]
            except:
                msg = kwargs["messages"]
                del kwargs["messages"]

        if isinstance(msg, str):
            ch = ChatHistory().add(CHAT_ROLE.USER, msg)
        else:
            assert isinstance(msg, dict)
            ch = ChatHistory.from_history_dict(msg)

        chat_id = client.send_history(None,
                            ch,
                            generation_settings={**kwargs},
                            blocking=True
                            )  # chat_history_with_images)
        return None, client.get_chat_messages(chat_id).history[-1]["content"]

if __name__ == "__main__":
    print(ChatCompletion.create("Hello, how are you?"))