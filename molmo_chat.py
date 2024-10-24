# https://github.com/allenai/OLMo
import requests
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from PIL import Image

#from transformers import pipeline
#olmo_pipe = pipeline("text-generation", model="allenai/OLMo-1B-0724-hf")
#print(olmo_pipe("Language modeling is"))


#from transformers import AutoModelForCausalLM, AutoTokenizer

#olmo = AutoModelForCausalLM.from_pretrained("allenai/OLMo-1B-0724-hf")
#tokenizer = AutoTokenizer.from_pretrained("allenai/OLMo-1B-0724-hf")

#message = ["We will test your cognition abilities.\n\nHere are your possible actions: A) Pick up. B) Place.\n\nHere is a description of the game board: there are two spots to place cubes (spot Alpha and spot Beta).\n\nHere is a description of the game board's state: on Alpha, there are three stacked cubes, in order, red, green, blue. Spot Beta is empty,\n\n You must use actions (A) and (B) to obtain a tower of cubes, in order, green, blue, red.\n\nNow tell me the sequence of actions you wish to apply."]
#inputs = tokenizer(message, return_tensors='pt', return_token_type_ids=False)
#response = olmo.generate(**inputs, max_new_tokens=500, do_sample=True, top_k=50, top_p=0.95)
#print(tokenizer.batch_decode(response, skip_special_tokens=True)[0])


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

# load the processor
processor = AutoProcessor.from_pretrained(
    'allenai/Molmo-7B-D-0924', # 'allenai/Molmo-7B-D-0924'
    trust_remote_code=True,
    torch_dtype='auto',
    device_map='auto'
)

# load the model
model = AutoModelForCausalLM.from_pretrained(
    'allenai/Molmo-7B-D-0924', # 'allenai/Molmo-7B-D-0924'
    trust_remote_code=True,
    torch_dtype='auto',
    device_map='auto'
)

url = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
image = Image.open(requests.get(url, stream=True).raw)
inputs = processor.process(text='Describe the image', images=[image], padding=True, return_tensors="pt")

inputs = {k: v.to(model.device).unsqueeze(0) for k, v in inputs.items()}


with torch.autocast(device_type="cuda", enabled=True, dtype=torch.bfloat16):
  output = model.generate_from_batch(
      inputs,
      GenerationConfig(max_new_tokens=500, stop_strings="<|endoftext|>"),
      tokenizer=processor.tokenizer
  )

# only get generated tokens; decode them to text
generated_tokens = output[0,inputs['input_ids'].size(1):]
generated_text = processor.tokenizer.decode(generated_tokens, skip_special_tokens=True)

# print the generated text
print(generated_text)
