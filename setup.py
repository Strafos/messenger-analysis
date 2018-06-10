import os
import re
from pprint import pprint

from helpers import get_json, check_participants
from message_analysis import count_messages

BASE_DIR = "/home/zaibo/code/fb_analysis/data"
MY_NAME = "Zaibo Wang"

def generater_friends(n=50):
    """
    Generate friends.py which is used by most of the other scripts
    friends.py will contain paths to the top n most frequently messaged friends
    """
    all_paths = []
    for dir in os.listdir(BASE_DIR):
        inner_dir = BASE_DIR + "/" + dir
        for filename in os.listdir(inner_dir):
            if filename == "message.json":
                filepath = inner_dir + "/" + filename
                all_paths.append(filepath)

    # Each element is a tuple of (friend_name, total_messages)
    messages_per_friend = []

    for path in all_paths:
        message_json = get_json(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            participant = message_json.get("participants")[0]
            total_messages = count_messages(messages)
            messages_per_friend.append((participant, total_messages, path))
    messages_per_friend.sort(key=lambda x: x[1], reverse=True)

    name_pattern = "(?P<first_name>[A-Z]*) (?P<last_name>[A-Z]*)"
    with open("friends.py", "w") as f:
        names = []
        for name, _, path in messages_per_friend[:n]:
            name = name.upper()
            regex = re.match(name_pattern, name)
            parsed_name = "_".join([regex.group("first_name"), regex.group("last_name")])
            write_wrapper(f, parsed_name, path)
            names.append((name, path))
        f.write("ALL_FRIENDS = %s\n" % str(names))

def generate_groupchats():
    """
    Use find_groupchat() to get groupchat paths and hardcode them to this function
    to append them to the end of friends.py
    """
    with open("friends.py", "a") as f:
        name = "situation_room"
        path = "/home/zaibo/code/fb_analysis/data/thesituationroom_69ae5d10b1/message.json"
        write_wrapper(f, name, path)

        name = "eggplant"
        path = "/home/zaibo/code/fb_analysis/data/96a68cd96d/message.json"
        write_wrapper(f, name, path)

def generate_name():
    with open("friends.py", "a") as f:
        write_wrapper(f, "MY_NAME", MY_NAME)

def find_groupchat():
    """
    genereate will not generate group chats, so we must find them manually
    We can set up conditions to narrow down the chats (ex: find all groupchats with 15+ people)
    """
    all_paths = []
    for dir in os.listdir(BASE_DIR):
        inner_dir = BASE_DIR + "/" + dir
        for filename in os.listdir(inner_dir):
            if filename == "message.json":
                filepath = inner_dir + "/" + filename
                all_paths.append(filepath)

    for path in all_paths:
        message_json = get_json(path)
        party = message_json.get("participants", "")
        # Make some condition to look for group chats
        if len(party) > 15:
            print(path)

def write_wrapper(f, variable, value):
    f.write("%s = \"%s\"\n" % (variable, value))

generater_friends(50)
generate_groupchats()
generate_name()