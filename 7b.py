import torch
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from PIL import Image
import requests

# load the processor
processor = AutoProcessor.from_pretrained(
    'allenai/Molmo-72B-0924', # 'allenai/Molmo-7B-D-0924'
    trust_remote_code=True,
    torch_dtype='auto',
    device_map='auto'
)

images = [Image.open("./block-tower.jpg")]
query = """
    Describe the image. 
    """
inputs = processor.process(
    images=images,
    text=query
)


model = AutoModelForCausalLM.from_pretrained(
    'allenai/Molmo-72B-0924', # 'allenai/Molmo-7B-D-0924'
    trust_remote_code=True,
    torch_dtype='auto',
    device_map='auto'
)

# move inputs to the correct device and make a batch of size 1
inputs = {k: v.to(model.device).unsqueeze(0) for k, v in inputs.items()}

with torch.autocast(device_type="cuda", enabled=True, dtype=torch.bfloat16):
  output = model.generate_from_batch(
      inputs,
      GenerationConfig(max_new_tokens=500, stop_strings="<|endoftext|>"),
      tokenizer=processor.tokenizer
  )

# generate output; maximum 200 new tokens; stop generation when <|endoftext|> is generated
#output = model.generate_from_batch(
#    inputs,
#    GenerationConfig(max_new_tokens=200, stop_strings="<|endoftext|>"),
#    tokenizer=processor.tokenizer
#)

# only get generated tokens; decode them to text
generated_tokens = output[0,inputs['input_ids'].size(1):]
generated_text = processor.tokenizer.decode(generated_tokens, skip_special_tokens=True)

# print the generated text
print(generated_text)

# >>>  This image features an adorable black Labrador puppy, captured from a top-down
#      perspective. The puppy is sitting on a wooden deck, which is composed ...
