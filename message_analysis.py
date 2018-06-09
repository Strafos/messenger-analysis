import json
import os
import datetime
from pprint import pprint
from tabulate import tabulate

import config

def get_json(path):
    with open(path, "r") as f:
        return json.loads(f.read())

def check_participants(message_json):
    return len(message_json.get("participants", [])) == 1

def datetime_from_mtime(mtime):
    return datetime.datetime.fromtimestamp(mtime)

def message_freq(messages, participant):
    # After a gap in talking, who initiates first?
    # Obvious problem is conversations can go on hiatus for a couple days
    gaps = [.01, 1, 2, 5, 10]
    tdelta_gaps = [datetime.timedelta(days=i) for i in gaps]

    print("Gap\tZaibo Count\t%s Count\tZaibo %%\t %s %%" % (participant, participant))
    for gap, gap_in_days in zip(tdelta_gaps, gaps):
        prev_msg_t = datetime_from_mtime(messages[-1]["timestamp"])
        counters = {
            "Zaibo Wang": 0,
            participant: 0 # Other participant. We assume there is only one
        }
        for message in reversed(messages):
            curr_msg_t = datetime_from_mtime(message["timestamp"])
            sender = message["sender_name"]
            t_delta = curr_msg_t - prev_msg_t
            if t_delta > gap:
                counters[sender] += 1
            prev_msg_t = curr_msg_t
        total_count = sum(counters.values()) + 1
        print("%f\t%d\t%d\t%f\t%f" % (gap_in_days, 
                                      counters["Zaibo Wang"], 
                                      counters[participant], 
                                      counters["Zaibo Wang"]/total_count,
                                      counters[participant]/total_count))

def average_response_time(messages, participant):
    data = {
        "Zaibo Wang": {
            "response_time": datetime.timedelta(days=0).total_seconds(),
            "responses": 0
        },
        participant: {
            "response_time": datetime.timedelta(days=0).total_seconds(),
            "responses": 0
        }
    }
    first_message = messages[-1]
    prev_msg_t = datetime_from_mtime(first_message["timestamp"])
    prev_sender = first_message["sender_name"]
    for message in reversed(messages):
        curr_msg_t = datetime_from_mtime(message["timestamp"])
        curr_sender = message["sender_name"]
        if curr_sender != prev_sender:
            t_delta = curr_msg_t - prev_msg_t
            data[curr_sender]["response_time"] += t_delta.total_seconds()
            data[curr_sender]["responses"] += 1
        prev_msg_t = curr_msg_t
        prev_sender = curr_sender
    for k, v in data.items():
        # if k != "Zaibo Wang":
        print(k, v["response_time"]//60/v["responses"])

def sanity_check(messages):
    counters = {}
    for message in messages:
        sender = message["sender_name"]
        counters[sender] = 1 if sender not in counters else counters[sender] + 1
    print("sanity check", counters)

def count_messages(messages):
    counters = {}
    participants = set()
    for message in messages:
        sender = message["sender_name"]
        participants.add(sender)
        counters[sender] = 1 if sender not in counters else counters[sender] + 1
    return sum(counters.values()) if len(participants) == 2 else 0

def count_messages_group(messages):
    counters = {}
    for message in messages:
        sender = message["sender_name"]
        counters[sender] = 1 if sender not in counters else counters[sender] + 1
    tot = sum([v for k, v in counters.items()])
    print_list = []
    for name, val in counters.items():
        print_list.append([name, val, float("%.2f" % (val/tot))])
    print_list.sort(key=lambda x: x[1], reverse=True)
    print(tabulate(print_list, headers=["Name", "# of messages", "%% of all messages"]))
    return counters

def count_characters_group(messages):
    counters = {}
    for message in messages:
        sender = message["sender_name"]
        chars = len(message.get("content", ""))
        counters[sender]["characters"] = chars if sender not in counters else counters[sender]["characters"] + chars
    tot = sum([v for k, v in counters.items()])
    print_list = []
    for name, val in counters.items():
        print_list.append([name, val, float("%.2f" % (val/tot))])
    print_list.sort(key=lambda x: x[1], reverse=True)
    print(tabulate(print_list, headers=["Name", "# of characters", "%% of all characters"]))
    return counters

def generate_normalization(messages):
    counters = {}
    for message in messages:
        sender = message["sender_name"]
        counters[sender] = 1 if sender not in counters else counters[sender] + 1

def average_message_len_simple(messages, participant):
    """
    Looks at each message with no aggregation (basically everytime you press enter)
    Uses character count
    """

    data = {
        "Zaibo Wang": {
            "total_length": 0,
            "message_count": 0
        },
        participant: {
            "total_length": 0,
            "message_count": 0
        }
    }
    for message in messages:
        data[message["sender_name"]]["total_length"] += len(message.get("content", ""))
        data[message["sender_name"]]["message_count"] += 1
    for name, counts in data.items():
        print("%s simple average message length: %f" % (name, counts["total_length"]/counts["message_count"]))

def average_message_word_count_simple(messages, participant):
    """
    Looks at each message with no aggregation (basically everytime you press enter)
    Uses word count
    """

    data = {
        "Zaibo Wang": {
            "total_words": 0,
            "message_count": 0
        },
        participant: {
            "total_words": 0,
            "message_count": 0
        }
    }
    for message in messages:
        data[message["sender_name"]]["total_words"] += len(message.get("content", "").split(" "))
        data[message["sender_name"]]["message_count"] += 1
    for name, counts in data.items():
        print("%s simple average message word count: %f" % (name, counts["total_words"]/counts["message_count"]))

def average_message_len_aggregate(messages, participant):
    """
    Here, we define a message as all the characters sent before a message from the other person

    Noted error that the last message cluster is not aggregated
    """
    data = {
        "Zaibo Wang": {
            "total_length": 0,
            "message_count": 0
        },
        participant: {
            "total_length": 0,
            "message_count": 0
        }
    }
    prev_sender = "Zaibo Wang"
    buffered_len = 0
    for message in messages:
        curr_sender = message["sender_name"]
        if curr_sender != prev_sender:
            data[prev_sender]["total_length"] += buffered_len
            data[prev_sender]["message_count"] += 1
            buffered_len = len(message.get("content", ""))
        else:
            buffered_len += len(message.get("content", ""))
        prev_sender = curr_sender

    for name, counts in data.items():
        print("%s aggregated average message length: %f" % (name, counts["total_length"]/counts["message_count"]))
    
def average_message_word_count_aggregate(messages, participant):
    """
    Words are naively defined by splitting the string into spaces

    Noted error that the last message cluster is not aggregated
    """
    data = {
        "Zaibo Wang": {
            "total_words": 0,
            "message_count": 0
        },
        participant: {
            "total_words": 0,
            "message_count": 0
        }
    }
    prev_sender = "Zaibo Wang"
    buffered_word_count = 0
    for message in messages:
        curr_sender = message["sender_name"]
        if curr_sender != prev_sender:
            data[prev_sender]["total_words"] += buffered_word_count
            data[prev_sender]["message_count"] += 1
            buffered_word_count = len(message.get("content", "").split(" "))
        else:
            buffered_word_count += len(message.get("content", "").split(" "))
        prev_sender = curr_sender

    for name, counts in data.items():
        print("%s aggregated average message word count: %f" % (name, counts["total_words"]/counts["message_count"]))

def specific_word_count(messages, participant, normalize=None):
    """
    TODO normalization by message count
    """
    words = ["lol", "lmao"]
    data = {
        "Zaibo Wang": {
            "word_count": 0
        },
        participant: {
            "word_count": 0
        }
    }
    for keyword in words:
        for message in messages:
            sender = message["sender_name"]
            content = message.get("content", "")
            count = content.lower().count(keyword)
            data[sender]["word_count"] += count
        for name, counts in data.items():
            print("keyword: %s, %s count: %d" % (keyword, name, counts["word_count"]))

# features
# longest dry spell
# average message length
# "enters" per response
# Average response time

def cluster_message_group(messages):
    """
    One cluster is all the messages sent before being interupted by someone else

    Noted error that the last message cluster is not aggregated
    """
    data = {}
    prev_sender = messages[-1]["sender_name"]
    for message in messages:
        curr_sender = message["sender_name"]
        if curr_sender != prev_sender:
            data[prev_sender] = 1 if not data.get(prev_sender) else data[prev_sender] + 1
        prev_sender = curr_sender

    tot = sum([val for key, val in data.items()])
    print_list = []
    for name, val in data.items():
        print_list.append([name, val, float("%.2f" % (val/tot))])
    print_list.sort(key=lambda x: x[1], reverse=True)
    print(tabulate(print_list, headers=["Name", "# cluster messages", "% cluster messages"]))

def main():
    # path = "data/" + JAIDEV_PHADKE + "/message.json"
    for person in config.people:
        path = "data/" + person + "/message.json"
        message_json = get_json(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            participant = message_json.get("participants")[0]
            # message_freq(messages, participant)
            # average_message_len_simple(messages, participant)
            # average_message_len_aggregate(messages, participant)
            # average_message_word_count_simple(messages, participant)
            # average_message_word_count_aggregate(messages, participant)
            # specific_word_count(messages, participant)
            average_response_time(messages, participant)
            # sanity_check(messages)

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
            messages_per_friend.append((participant, total_messages))
    messages_per_friend.sort(key=lambda x: x[1], reverse=True)
    # pprint(messages_per_friend[:n])
    count = 1
    for i in messages_per_friend[:n]:
        print(count, i)
        count += 1

    # pprint(messages_per_friend)

def find_groupchat():
    # Find groupchat by some condition
    base_dir = "data"
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
        # Make some condition to look for group chats
        if len(party) > 15:
            print(path)

def group_chat_analysis():
    message_json = get_json(config.situation_room)
    messages = message_json.get("messages", [])
    # count_messages_group(messages)
    # count_characters_group(messages)
    # cluster_message_group(messages)
    groupchat_message_stats(messages)

def groupchat_message_stats(messages):
    """
    counters = {
        "characters": {
            "Person 1": 100,
            "Person 2": 50
        },
        "messages": {
            "Person 1": 200,
            "Person 2": 100
        }
    }
    """
    # Get count of characters, messages, message clusters
    counters = {
        "characters": {},
        "messages": {},
        "clusters": {}
    }
    prev_sender = messages[-1]["sender_name"]
    for message in messages:
        sender = message["sender_name"]
        chars = len(message.get("content", ""))
        counters["characters"][sender] = chars if not counters["characters"].get(sender) else counters["characters"].get(sender) + chars
        counters["messages"][sender] = 1 if not counters["messages"].get(sender) else counters["messages"].get(sender) + 1
        if sender != prev_sender:
            counters["clusters"][sender] = 1 if not counters["clusters"].get(sender) else counters["clusters"].get(sender) + 1
        prev_sender = sender

    total_clusters = sum([v for k, v in counters["clusters"].items()])
    total_messages = sum([v for k, v in counters["messages"].items()])
    total_characters = sum([v for k, v in counters["characters"].items()])
    print_list = []
    for messages, chars, clusters in zip(counters["messages"].items(), counters["characters"].items(), counters["clusters"].items()):
        # messages, chars, clusters are a tuple of (<Name>, <Count>)
        # Ex: ("Zaibo Wang", 500)
        name = messages[0]
        print_list.append([name, 
                           float("%.2f" % (chars[1]/total_characters)), 
                           float("%.2f" % (messages[1]/total_messages)),
                           float("%.2f" % (clusters[1]/total_clusters))])
    print_list.sort(key=lambda x: x[1], reverse=True)
    print(tabulate(print_list, headers=["Name", "% characters", "% messages", "% clusters"]))
        
# group_chat_analysis()
most_messaged_friends(50)
# main()