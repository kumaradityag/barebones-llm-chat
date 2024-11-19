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
    max_new_tokens:int = 512
    do_sample:bool = True
    top_k:int = 50
    top_p:float = 0.95

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

class Olmo(_Bot):
    def __init__(self, model_string="allenai/OLMo-7B-0724-Instruct-hf", precision=torch.bfloat16):
        super().__init__(model_string, precision)

        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.model = AutoModelForCausalLM.from_pretrained(
            model_string, 
            trust_remote_code=True,
            torch_dtype='auto',
            device_map='auto'
            ).to(dtype=self.precision)
        self.tokenizer = AutoTokenizer.from_pretrained(model_string, 
                                                       trust_remote_code=True,
                                                       torch_dtype='auto',
            device_map='auto'
            )
        print("Olmo loaded")

    def respond(self, chat, images=None, generation_settings=None):
        if images is not None:
            print("Images found, but Olmo is not multimodal. Images will be ignored.", file=sys.stderr)

        _generation_settings = vars(DefaultOlmoSettings())
        if generation_settings is not None:
            _generation_settings.update(**generation_settings)
        del generation_settings

        print()
        print("-----")
        print("Generating with following settings:")
        print(_generation_settings)
        print("-----")
        print()

        messages = chat.to_lowercase_roles().history_without_images

        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")

        #inputs = self.tokenizer(messages, return_tensors='pt', return_token_type_ids=False)
        #inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        inputs = inputs.to(self.model.device)

        # optional verifying cuda
        # inputs = {k: v.to('cuda') for k,v in inputs.items()}
        # olmo = olmo.to('cuda')
        response = self.model.generate(input_ids=inputs, **_generation_settings)
        
        response = response[:,inputs.shape[1]:]
        generated_text = self.tokenizer.batch_decode(response, skip_special_tokens=True)[0]

        chat = chat.add(CHAT_ROLE.ASSISTANT, generated_text)
        return chat