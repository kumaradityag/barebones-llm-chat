import torch
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from PIL import Image
import requests

# load the processor
processor = AutoProcessor.from_pretrained(
    'allenai/Molmo-7B-D-0924',
    trust_remote_code=True,
    torch_dtype='auto',
    device_map='auto'
)

# load the model
model = AutoModelForCausalLM.from_pretrained(
    'allenai/Molmo-7B-D-0924',
    trust_remote_code=True,
    torch_dtype='auto',
    device_map='auto'
)

# process the image and text
#url_images = ["https://www.youcubed.org/wp-content/uploads/2017/03/block-tower.jpg"]
#images = []
#for url in url_images:
#    images.append(
#        Image.open(requests.get(url).raw)
#    )

images = [Image.open("./block-tower.jpg")]

inputs = processor.process(
    images=[images],
    text="You have access to two 'spots' to place blocks: spot Alpha and Spot Beta. The tower in the photo is on spot Alpha. You can only manipulate one block at once. Provide a sequence of actions to re-arange to blocks such that now blue is on the bottom, red middle, yellow top."
)

# move inputs to the correct device and make a batch of size 1
inputs = {k: v.to(model.device).unsqueeze(0) for k, v in inputs.items()}

with torch.autocast(device_type="cuda", enabled=True, dtype=torch.bfloat16):
  output = model.generate_from_batch(
      inputs,
      GenerationConfig(max_new_tokens=200, stop_strings="<|endoftext|>"),
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
