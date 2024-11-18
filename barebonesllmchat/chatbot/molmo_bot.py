import dataclasses
from dataclasses import dataclass
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from PIL import Image
import requests

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from barebonesllmchat.common.chat_history import CHAT_ROLE, ChatHistory

from dataclasses import dataclass

@dataclass
class DefaultOlmoSettings:
    max_new_tokens=512
    temperature=1.0

    def replace(self, **kwargs):
        return dataclasses.replace(self, **kwargs)

class Olmo:
    def __init__(self, model_string='allenai/Molmo-7B-D-0924', precision=torch.bfloat16):
        self.processor = AutoProcessor.from_pretrained(
            model_string,
            trust_remote_code=True,
            torch_dtype='auto',
            device_map='auto'
        )

        self.precision = precision

        self.model = AutoModelForCausalLM.from_pretrained(
            'allenai/Molmo-7B-D-0924',  # 'allenai/Molmo-7B-D-0924'
            trust_remote_code=True,
            torch_dtype='auto',
            device_map='auto'
        ).to(dtype=self.precision)


    def respond(self, chat, images=None, generation_settings=None):
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

        inputs = self.processor.process(
            images=images, #chat.images,
            text=chat.pack(),
            message_format=None
        )
        inputs = {k: v.to(self.model.device).unsqueeze(0) for k, v in inputs.items()}
        if "images" in inputs:
            inputs["images"] = inputs["images"].to(self.precision)

        output = self.model.generate_from_batch(
            inputs,
<<<<<<< HEAD
            GenerationConfig(max_new_tokens=500, stop_strings="<|endoftext|>"),
=======
            GenerationConfig(**generation_settings, stop_strings="<|endoftext|>"),
>>>>>>> 5c39f27b142bb64a1b325a614d4fce7c34828461
            tokenizer=self.processor.tokenizer
        )

        generated_tokens = output[0, inputs['input_ids'].size(1):]
        generated_text = self.processor.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        chat = chat.add(CHAT_ROLE.ASSISTANT, generated_text)
        return chat

