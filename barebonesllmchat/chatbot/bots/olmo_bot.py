import dataclasses
from dataclasses import dataclass
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from PIL import Image
import requests

import sys
import pathlib

from barebonesllmchat.chatbot.bots.bot import _Bot

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from barebonesllmchat.common.chat_history import CHAT_ROLE, ChatHistory

from dataclasses import dataclass

@dataclass
class DefaultOlmoSettings:
    max_new_tokens:int = 100
    do_sample:bool = True
    top_k:int = 50
    top_p:float = 0.95

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

class Olmo(_Bot):
    def __init__(self, model_string='allenai/Molmo-7B-D-0924', precision=torch.bfloat16):
        super().__init__(model_string, precision)

        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.olmo = AutoModelForCausalLM.from_pretrained(model_string)
        self.tokenizer = AutoTokenizer.from_pretrained(model_string)

    def respond(self, chat, images=None, generation_settings=None):
        if images is not None:
            print("Images found, but Olmo is not multimodal. Images will be ignored.", file=sys.stderr)

        if generation_settings is None:
            generation_settings = {**DefaultOlmoSettings()}
        else:
            generation_settings = DefaultOlmoSettings().replace(**generation_settings)

        print()
        print("-----")
        print("Generating with following settings:")
        print(generation_settings)
        print("-----")
        print()

        inputs = self.tokenizer(chat.pack(), return_tensors='pt', return_token_type_ids=False)
        # optional verifying cuda
        # inputs = {k: v.to('cuda') for k,v in inputs.items()}
        # olmo = olmo.to('cuda')
        response = self.olmo.generate(**inputs, )
        generated_text = self.tokenizer.batch_decode(response, skip_special_tokens=True)[0]

        chat = chat.add(CHAT_ROLE.ASSISTANT, generated_text)
        return chat