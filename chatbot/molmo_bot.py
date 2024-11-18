from dataclasses import dataclass
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from PIL import Image
import requests

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
import common
from common.chat_history import CHAT_ROLE, ChatHistory


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

    def respond(self, chat, images=None):
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
            GenerationConfig(max_new_tokens=500, stop_strings="<|endoftext|>"),
            tokenizer=self.processor.tokenizer
        )

        generated_tokens = output[0, inputs['input_ids'].size(1):]
        generated_text = self.processor.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        chat = chat.add(CHAT_ROLE.ASSISTANT, generated_text)
        return chat

