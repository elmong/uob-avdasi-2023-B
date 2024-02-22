import os
import json

root_path = os.path.abspath(os.path.dirname(__file__))
filesave_path = root_path+"\saved_global_var.json"

def save(list_of_dict):
    print("Saving Global Var to " + filesave_path)
    with open(filesave_path, 'w') as file:
        json.dump(list_of_dict, file)

def load():
    print("Loading Global Var from " + filesave_path)
    if os.path.exists(filesave_path):
        with open(filesave_path, 'r') as file:
            return json.load(file)
    else:
        print("File does not exist. Returning None.")
        return None