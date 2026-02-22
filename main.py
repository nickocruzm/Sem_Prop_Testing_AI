import os
from openai import OpenAI



MODEL = "gpt-5.2"
client = OpenAI(api_key=os.getenv("GPT_API_KEY"))

data_dir = "/Users/nickocruz/Developer/CS206/semantic_prop_project/python_programs/"
files = os.listdir(data_dir)
file_paths = [f'{data_dir}/{f}' for f in files]




for file_path in file_paths[:1]:
    with open(file_path, "r") as f:
        code = f.read()
    
    input_txt = f"""
    Look through the following Python program and identify semantic properties. 
    {code}
    """
    
    request = [{
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": input_txt
            }
        ]
    }]
    
    
    response = client.responses.create(
        model = MODEL,
        input = request
    )

    print(response.output_text)