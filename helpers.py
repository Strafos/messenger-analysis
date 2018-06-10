import json

def get_json(path):
    with open(path, "r") as f:
        return json.loads(f.read())

def check_participants(message_json):
    """To check 1 on 1 messages"""
    return len(message_json.get("participants", [])) == 1