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


class _Bot:
    def __init__(self, model_string, precision=torch.bfloat16):
        self.model_string = model_string
        self.precision = precision

    def respond(self, chat, images=None, generation_settings=None):
        raise NotImplementedError()