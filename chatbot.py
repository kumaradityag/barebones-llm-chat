# https://github.com/allenai/OLMo

from transformers import pipeline
olmo_pipe = pipeline("text-generation", model="allenai/OLMo-1B-0724-hf")
print(olmo_pipe("Language modeling is"))


from transformers import AutoModelForCausalLM, AutoTokenizer

olmo = AutoModelForCausalLM.from_pretrained("allenai/OLMo-1B-0724-hf")
tokenizer = AutoTokenizer.from_pretrained("allenai/OLMo-1B-0724-hf")

message = ["We will test your cognition abilities.\n\nHere are your possible actions: A) Pick up. B) Place.\n\nHere is a description of the game board: there are two spots to place cubes (spot Alpha and spot Beta).\n\nHere is a description of the game board's state: on Alpha, there are three stacked cubes, in order, red, green, blue. Spot Beta is empty,\n\n You must use actions (A) and (B) to obtain a tower of cubes, in order, green, blue, red.\n\nNow tell me the sequence of actions you wish to apply."]
inputs = tokenizer(message, return_tensors='pt', return_token_type_ids=False)
response = olmo.generate(**inputs, max_new_tokens=500, do_sample=True, top_k=50, top_p=0.95)
print(tokenizer.batch_decode(response, skip_special_tokens=True)[0])