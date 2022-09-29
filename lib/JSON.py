import json

def load(path):
    with open(path, "r") as f:
        data = json.load(f)
        return data

def dump(path, res):
    with open(path, "w") as f:
        json.dump(res, f, indent=1)