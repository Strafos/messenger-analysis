import os
import re
import argparse
import glob
from pprint import pprint

from helpers import get_json, count_messages, check_participants

my_name = None

"""
This file generates friends.py which is needed for all data analysis
"""

# To look at groupchats, use find_groupchat() in setup.py
# by adding your conditions to narrow down the search
# Then, add them to the GROUPCHATS list
GROUPCHATS = [
    # Format is a tuple (name, path):
    # ("situation_room", "/home/zaibo/code/fb_analysis/data/thesituationroom_69ae5d10b1/message.json"),
    # ("eggplant", "/home/zaibo/code/fb_analysis/data/96a68cd96d/message.json")
]


def find_groupchat():
    """
    generate will not generate group chats, so we must find them manually
    We can set up conditions to narrow down the chats (ex: find all groupchats with 15+ people)
    """
    all_paths = []
    for dir in os.listdir(base_dir):
        inner_dir = base_dir + "/" + dir
        for filename in os.listdir(inner_dir):
            if filename == "message.json":
                filepath = inner_dir + "/" + filename
                all_paths.append(filepath)

    for path in all_paths:
        message_json = get_json(path)
        party = message_json.get("participants", "")
        # Make some condition to look for group chats, this one is 15+ participants
        if len(party) > 15:
            print(path)


def generate_friends(n=50):
    """
    Generate friends.py which is used by most of the other scripts
    friends.py will contain paths to the top n most frequently messaged friends
    """
    all_paths = []
    for dir in os.listdir(base_dir):
        if dir.startswith("."):  # Macs have a .DS_STORE file which throws an exception
            continue
        inner_dir = base_dir + "/" + dir
        for filename in os.listdir(inner_dir):
            if filename == "message.json":
                filepath = inner_dir + "/" + filename
                all_paths.append(filepath)

    # Each element is a tuple of (friend_name, total_messages)
    messages_per_friend = []

    for path in all_paths:
        message_json = get_json(path)
        print(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            participant = message_json.get("participants")
            participant = [i for i in participant if i['name'] != my_name]
            if len(participant) != 1:
                continue
            participant = participant[0]['name']
            total_messages = count_messages(messages)
            if total_messages != 0:
                messages_per_friend.append((participant, total_messages, path))
    messages_per_friend.sort(key=lambda x: x[1], reverse=True)

    # People have weird names, this regex can break...
    name_pattern = "(?P<first_name>([A-Z]|-)*) (?P<last_name>([A-Z]|-)*)"
    with open("friends.py", "w") as f:
        # Create a "BEST_FRIEND" which will be the default path
        # BEST_FRIEND is the most messaged friend
        _, _, path = messages_per_friend[0]
        write_wrapper(f, "BEST_FRIEND", path)

        names_and_paths = []
        paths = []
        for name, _, path in messages_per_friend[:n]:
            name = name.upper()
            regex = re.match(name_pattern, name)
            if not regex:
                continue
            # Some people have weird names, I did not handle edge cases
            parsed_name = "_".join(
                [regex.group("first_name"), regex.group("last_name")])
            parsed_name = parsed_name.replace(" ", "_").replace("-", "_")

            write_wrapper(f, parsed_name, path)

            names_and_paths.append((name, path))
            paths.append(path)
        f.write("ALL_FRIENDS = %s\n" % str(names_and_paths))
        f.write("ALL_FRIEND_PATHS = %s\n" % str(paths))


def generate_groupchats():
    """
    Use find_groupchat() to get groupchat paths and hardcode them to this function
    to append them to the end of friends.py
    """
    with open("friends.py", "a") as f:
        for name, path in GROUPCHATS:
            write_wrapper(f, name, path)


def generate_name():
    with open("friends.py", "a") as f:
        write_wrapper(f, "MY_NAME", my_name)


def write_wrapper(f, variable, value):
    f.write("%s = \"%s\"\n" % (variable, value))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Configs for setting up data source')
    parser.add_argument(
        '--dir', help="Path to unzipped messages directory", required=True)
    parser.add_argument(
        '--name', help="Your name in the format 'John Smith'", required=True)
    args = parser.parse_args()

    base_dir = args.dir
    my_name = args.name

    generate_friends(50)
    generate_groupchats()
    generate_name()
