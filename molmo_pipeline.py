import torch
from transformers import pipeline

chat = [
    {
        "role":"user",
        "content":[
            {
                "type":"image",
            },
            {
                "type":"text",
                "text":"Describe this image."
            }
        ]
    }
]

pipe = pipeline("text-generation", "allenai/Molmo-7B-D-0924", torch_dtype=torch.bfloat16, device_map="auto")
response = pipe(chat, max_new_tokens=512)

print(response[0]['generated_text'][-1]['content'])


print("PRINTING RESPONSE OBJECT")
print(response)
print("DONE")

chat = response[0]['generated_text']
chat.append(
    {"role": "user", "content": "Wait, what's so wild about soup cans?"}
)
response = pipe(chat, max_new_tokens=512)
print(response[0]['generated_text'][-1]['content'])