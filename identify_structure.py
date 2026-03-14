from tree_sitter import Language, Parser
from dotenv import load_dotenv
import tree_sitter_python
import os
import json

load_dotenv('.env')
python_dir = os.getenv("PROGRAMS_DIR", "dir-absent")
logs_dir = os.getenv("LOGS_DIR",'no-logs-dir')


results = {}

def extract_structure(node, code_bytes, structure):
    if node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        if name_node:
            structure["functions"].append(
                code_bytes[name_node.start_byte:name_node.end_byte].decode()
            )

    if node.type == "if_statement":
        cond = node.child_by_field_name("condition")
        if cond:
            structure["branches"].append(
                code_bytes[cond.start_byte:cond.end_byte].decode()
            )

    if node.type in ("for_statement", "while_statement"):
        structure["loops"].append(node.type)

    if node.type == "return_statement":
        structure["returns"] += 1

    for child in node.children:
        extract_structure(child, code_bytes, structure)

PY_LANGUAGE = Language(tree_sitter_python.language())
parser = Parser(PY_LANGUAGE)

#parser.language = tree_sitter_python.language()

for filename in os.listdir(python_dir)[:5]:
    if not filename.endswith(".py"): continue
    
    filepath = os.path.join(python_dir, filename)
    with open(filepath, "rb") as f:
        code = f.read()
    
    structure = {
        "functions": [],
        "branches": [],
        "loops": [],
        "returns": 0
    }
    
    tree = parser.parse(code)
    root = tree.root_node
    extract_structure(root, code, structure)
    results[filename] = structure

output_path = os.path.join(logs_dir, "structure.json")
with open(output_path, "w") as out:
    json.dump(results, out, indent=2)
