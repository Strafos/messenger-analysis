import os
import re
from collections import defaultdict
from pprint import pprint

import matplotlib.pyplot as plt
from tabulate import tabulate

from helpers import get_json
from name_hash import NameHasher
import friends


ANONYMOUS = False
nh = NameHasher()


def main(path):
    message_json = get_json(path)
    messages = message_json.get("messages", [])
    # groupchat_message_stats(messages)
    karma_stats(messages)


def karma_stats(messages):
    """
    Creates dictionary of counter + cluster + message + links data of all members of a group chat
    and displays data as table and pie chart
    """
    name_map = {
        "zaibo": 0,
        "zaibo wang": 0,
        "rishi": 1,
        "rishi tripathy": 1,
        "eric": 2,
        "eric li": 2,
        "jaidev": 3,
        "jaidev phadke": 3,
    }
    # matrix = [["-", "Z", "R", "E", "J"], ["Z", 0, 0, 0, 0], [
    #     "R", 0, 0, 0, 0], ["E", 0, 0, 0, 0], ["J", 0, 0, 0, 0]]
    matrix = [["-", "Z", "R", "E", "J"], ["Z", (0, 0), (0, 0), (0, 0), (0, 0)], [
        "R", (0, 0), (0, 0), (0, 0), (0, 0)], ["E", (0, 0), (0, 0), (0, 0), (0, 0)], ["J", (0, 0), (0, 0), (0, 0), (0, 0)]]
    events = {}
    counters = defaultdict(int)
    for message in messages:
        karma_re = r'(?i)(\-\-|\+\+)'
        # karma_re = r'(?i)(jaidev|jaidev phadke|zaibo|zaibo wang|rishi|rishi tripathy|eric|eric li)( ?)(\-\-|\+\+)'
        sender = message.get("sender_name", None)
        timestamp = message.get("timestamp_ms", None)
        content = message.get("content", "")
        if content:
            regex = re.findall(karma_re, content)
            if regex:
                print(message)
                # for receiver, _, inc in regex:
                #     receiver_val = name_map[receiver.lower()]
                #     sender_val = name_map[sender.lower()]
                #     if receiver_val == 0 and 1 == sender_val:
                #         print(message)
                #     if inc == "++":
                #         pos, neg = matrix[sender_val+1][receiver_val+1]
                #         matrix[sender_val+1][receiver_val+1] = (pos+1, neg)
                #     elif inc == "--":
                #         pos, neg = matrix[sender_val+1][receiver_val+1]
                #         matrix[sender_val+1][receiver_val+1] = (pos, neg-1)
    # print('\n'.join([str(row) for row in matrix]))
    # print(''.join('{:5}'.format(x) for x in ["-", "Z", "R", "E", "J"]))
    # print('\n'.join([''.join(['{:4}'.format(item) for item in row])
    #                  for row in matrix[1:]]))


def groupchat_message_stats(messages):
    """
    Creates dictionary of counter + cluster + message + links data of all members of a group chat
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
    link_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    counters = defaultdict(lambda: defaultdict(int))
    prev_sender = messages[-1]["sender_name"]
    for message in messages:
        sender = message["sender_name"]

        if ANONYMOUS:
            sender = nh.hash_by_name(sender)

        content = message.get("content", "")

        # Aggregate characters
        chars = len(content)
        counters["characters"][sender] = chars if not counters["characters"].get(
            sender) else counters["characters"].get(sender) + chars

        # Aggregate messages
        counters["messages"][sender] = 1 if not counters["messages"].get(
            sender) else counters["messages"].get(sender) + 1

        # Aggregate clusters
        if sender != prev_sender:
            counters["clusters"][sender] = 1 if not counters["clusters"].get(
                sender) else counters["clusters"].get(sender) + 1

        # Aggregate links
        num_links = len(re.findall(link_re, content))
        counters["links"][sender] += num_links

        prev_sender = sender

    total_clusters = sum([v for k, v in counters["clusters"].items()])
    total_messages = sum([v for k, v in counters["messages"].items()])
    total_characters = sum([v for k, v in counters["characters"].items()])
    total_links = sum([v for k, v in counters["links"].items()])

    # Assemble data in print_list format to print out as table
    print_list = []
    for messages, chars, clusters, links in zip(counters["messages"].items(),
                                                counters["characters"].items(),
                                                counters["clusters"].items(),
                                                counters["links"].items()):
        # messages, chars, clusters are a tuple of (<Name>, <Count>)
        # Ex: ("Zaibo Wang", 500)
        name = messages[0]
        print_list.append([name,
                           float("%.3f" % (chars[1]/total_characters)),
                           float("%.3f" % (messages[1]/total_messages)),
                           float("%.3f" % (clusters[1]/total_clusters)),
                           float("%.3f" % (links[1]/total_links))])
    print_list.sort(key=lambda x: x[1], reverse=True)
    print(tabulate(print_list, headers=[
          "Name", "% characters", "% messages", "% clusters", "% links"]))

    # Generate pie charts
    labels = [x[0] for x in print_list]
    characters = [x[1] for x in print_list]
    messages = [x[2] for x in print_list]
    clusters = [x[3] for x in print_list]
    links = [x[4] for x in print_list]

    ax1 = plt.subplot(411)
    ax1.pie(characters, labels=labels, autopct='%1.2f%%',
            startangle=90)
    ax1.axis('equal')
    plt.title("Characters", fontsize=20)

    ax1 = plt.subplot(412)
    ax1.pie(clusters, labels=labels, autopct='%1.2f%%',
            startangle=90)
    ax1.axis('equal')
    plt.title("Clusters", fontsize=20)

    ax1 = plt.subplot(413)
    ax1.pie(messages, labels=labels, autopct='%1.2f%%',
            startangle=90)
    ax1.axis('equal')
    plt.title("Messages", fontsize=20)

    ax1 = plt.subplot(414)
    ax1.pie(links, labels=labels, autopct='%1.2f%%',
            startangle=90)
    ax1.axis('equal')
    plt.title("Links", fontsize=20)

    plt.show()


if __name__ == "__main__":
    # path = friends.situation_room
    # path = friends.eggplant
    path = "./situationroom_7_29_18.json"
    main(path)
