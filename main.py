import os



import requests
import json
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3:mini"

PROMPT_TEMPLATE = """

Identify sturctural elements that exist in the program. Look for the following:

- functions or methods
- control-flow branches
- loops
- API call boundaries (pre/post conditions)
- early returns

output results as JSON


Example:

Program: 
def normalize(xs):
    if len(xs) == 0:
        return xs
    s = sum(xs)
    return [x  / s for x in xs]

Output:


function: normalize(xs)
Branch 1: len(xs) == 0
Branch 2: len(xs) > 0

Now Identify the structural elements for the following program.

Program:
{code}

Output:
"""


def warm_model():
    requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": "hi",
            "stream": False,
            "options": {
                "num_predict": 1
            }
        }
    )

def query_model(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "num_predict": 100,
                "temperature": 0,
                "num_ctx":2048
            }
        }
    )
    return response.json()


def run_batch(program_dir, out_dir="results"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    for filename in os.listdir(program_dir)[:1]:
        if filename.endswith(".py"):
            filepath = os.path.join(program_dir, filename)
            with open(filepath, "r") as f:
                code = f.read()
            prompt = PROMPT_TEMPLATE.format(code={code})
            print(prompt)
            result = query_model(prompt)
            outpath = os.path.join(out_dir, filename + ".result")
            with open(outpath, "w") as f:
                f.write(str(result))



if __name__ == "__main__":
    # loads model and preventing load time from occuring on a more complicate prompt.
    warm_model()
    data_dir = "/Users/nickocruz/Developer/CS206/semantic_prop_project/python_programs/"
    files = os.listdir(data_dir)
    file_paths = [f'{data_dir}/{f}' for f in files]
    run_batch(data_dir)