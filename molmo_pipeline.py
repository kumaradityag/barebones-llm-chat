import torch
from transformers import pipeline

chat = [
    {"role": "user", "content": "Hey, can you tell me any fun things to do in New York?"}
]

pipe = pipeline("text-generation", "allenai/Molmo-7B-D-0924", torch_dtype=torch.bfloat16, device_map="auto")
response = pipe(chat, max_new_tokens=512)