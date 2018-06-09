import os
import re
from pprint import pprint

from helpers import get_json, check_participants
from message_analysis import count_messages

def most_messaged_friends(n):
    # Return n most messaged friends and total number of messages between that friend
    base_dir = "data"
    all_paths = []
    for dir in os.listdir(base_dir):
        inner_dir = base_dir + "/" + dir
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
            f.write("%s = \"%s\"\n" % (parsed_name, path))
            names.append((name, path))
        f.write("ALL_FRIENDS = %s" % str(names))


most_messaged_friends(60)