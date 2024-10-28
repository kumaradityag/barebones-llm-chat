import random
from typing import List

# Lists of adjectives and nouns
adjectives = [
    "serene", "brave", "charming", "eager", "bold", "mighty", "gentle",
    "graceful", "bright", "lively", "creative", "elegant", "fearless", "charistmatic", "stupendous"
]
nouns = [
    "aardvark", "cactus", "dolphin", "eagle", "fox", "giraffe", "heron",
    "iguana", "jaguar", "koala", "lemur", "marmot", "narwhal"
]

# Generate a random name
def generate_name(existing_names: List[str]) -> str:
    existing_names = [None] + existing_names

    ret = None
    while ret in existing_names:
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        ret = f"{adjective}-{noun}-{random.randint(1,10)}"

    return ret
