import os

import matplotlib.pyplot as plt
from tabulate import tabulate

from helpers import get_json
import friends

def main(path):
    message_json = get_json(path)
    messages = message_json.get("messages", [])
    groupchat_message_stats(messages)

def groupchat_message_stats(messages):
    """
    Creates dictionary of counter + cluster + message data of all members of a group chat
    and displays data as table and pie chart

    Example
    counters = {
        "characters": {
            "Person 1": 100,
            "Person 2": 50
        },
        "clusters": {
            "Person 1": 100,
            "Person 2": 50
        },
        "messages": {
            "Person 1": 200,
            "Person 2": 100
        }
    }
    """
    counters = {
        "characters": {},
        "messages": {},
        "clusters": {}
    }
    prev_sender = messages[-1]["sender_name"]
    for message in messages:
        sender = message["sender_name"]
        chars = len(message.get("content", ""))

        # Aggregate characters
        counters["characters"][sender] = chars if not counters["characters"].get(sender) else counters["characters"].get(sender) + chars

        # Aggregate messages
        counters["messages"][sender] = 1 if not counters["messages"].get(sender) else counters["messages"].get(sender) + 1

        # Aggregate clusters
        if sender != prev_sender:
            counters["clusters"][sender] = 1 if not counters["clusters"].get(sender) else counters["clusters"].get(sender) + 1

        prev_sender = sender

    total_clusters = sum([v for k, v in counters["clusters"].items()])
    total_messages = sum([v for k, v in counters["messages"].items()])
    total_characters = sum([v for k, v in counters["characters"].items()])

    # Assemble data in print_list format to print out as table
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

    # Generate pie charts
    labels = [x[0] for x in print_list]
    characters = [x[1] for x in print_list]
    messages = [x[2] for x in print_list]
    clusters = [x[3] for x in print_list]

    ax1 = plt.subplot(311)
    ax1.pie(characters, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title("Characters")

    ax1 = plt.subplot(312)
    ax1.pie(clusters, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title("Clusters")

    ax1 = plt.subplot(313)
    ax1.pie(messages, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title("Messages")

    plt.show()

if __name__ == "__main__":
    path = friends.situation_room
    main(path)