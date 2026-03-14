import os
import requests
import json
from pathlib import Path
from ollama import chat
from pydantic import BaseModel
from typing import Literal


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"
VERSION = "00"
PART = "01"

PROJECT_DIR = "/Users/nickocruz/Developer/CS206/semantic_prop_project/"


PROMPT_TEMPLATE = """

Identify sturctural elements that exist in the program. Look for the following:

- functions
- control-flow branches
- loops
- API call boundaries (pre/post conditions)
- early returns 

Example:

def normalize(xs):
    if len(xs) == 0:
        return xs
    s = sum(xs)
    return [x  / s for x in xs]


Expected Output:

{
    {
        "scope": "function",
        "function": "normalize",
        "property": "unit_sum",
        "precondition": "sum(xs) != 0",
        "formal": "sum(normalize(xs)) == 1"
    }

    {
        "scope":"branch",
        "function":"normalize",
        "condition":"len(xs)==0",
        "property":"identity_on_empty"
        "formal": "normalize(xs) == xs"
    }
}

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


class SemanticProperty(BaseModel):
    scope: Literal["function", "branch"]
    function: str
    branches: list[str]
    loops: list[str]
    early_returns: list[str]


if __name__ == "__main__":
    # loads model and preventing load time from occuring on a more complicate prompt.
    #warm_model()
    DATA_DIR = f"{PROJECT_DIR}/python_programs/"
    
    out_dir = f"{PROJECT_DIR}/Sem_Prop_Testing_AI/results/v{VERSION}/Part{PART}/{MODEL}"
    
    files = os.listdir(DATA_DIR)
    file_paths = [f'{DATA_DIR}/{f}' for f in files]
    
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    
    program_dir = DATA_DIR
    for filename in os.listdir(program_dir)[:5]:
        print(filename)
        if filename.endswith(".py"):
            filepath = os.path.join(program_dir, filename)
            with open(filepath, "r") as f:
                code_str = f.read()
            
            prompt = PROMPT_TEMPLATE.replace("<<CODE>>", code_str)
            response = chat(
                model=MODEL,
                messages= [{'role':'user', 'content':prompt}],
                format=SemanticProperty.model_json_schema()
            )
            data = SemanticProperty.model_validate_json(response.message.content)
        
        outpath = os.path.join(out_dir, filename + ".json")
        with open(outpath, "w") as f:
            json.dump(data.model_dump(), f, indent=2)