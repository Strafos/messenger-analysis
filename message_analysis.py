import os
import datetime
from pprint import pprint
from tabulate import tabulate
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num
import pandas as pd

import friends
from helpers import get_json, check_participants

MY_NAME = "Zaibo Wang"

def main(path):
    # for person, path in friends.ALL_FRIENDS:
    for i in range(1):
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
            # average_response_time(messages, participant)
            # sanity_check(messages)
            # data = messages_over_time(messages)
            data = characters_over_time(messages)
    graph_stat_over_time(data, "characters")

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


def messages_over_time(messages, period="month"):
    """
    {
        "person": {
            datetime.datetime: message_number
        }
    }
    """
    data = defaultdict(lambda: defaultdict(int))
    for message in messages:
        m_time = datetime_from_mtime(message["timestamp"])
        if period == "Day":
            m_time = datetime.datetime(year=m_time.year, month=m_time.month, day=m_time.day)
            most_recent_period = datetime.datetime(year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day)
        elif period == "Month":
            m_time = datetime.datetime(year=m_time.year, month=m_time.month, day=1)
            most_recent_period = datetime.datetime(year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=1)
        elif period == "Year":
            m_time = datetime.datetime(year=m_time.year, month=1, day=1)
            most_recent_period = datetime.datetime(year=datetime.datetime.now().year, month=1, day=1)

        participant = message["sender_name"]
        data[participant][m_time] += 1
        data["total"][m_time] += 1
    return data

def characters_over_time(messages):
    """
    {
        "person": {
            datetime.datetime: character_count
        }
    }
    """
    data = defaultdict(lambda: defaultdict(int))
    for message in messages:
        participant = message["sender_name"]

        # Grab timestamp from message and cast it to a month + year timestamp
        timestamp = datetime_from_mtime(message["timestamp"])
        m_time = datetime.datetime(year=timestamp.year, month=timestamp.month, day=1)

        # We use this to get all messages from a certain month
        MESSAGE_DUMP = True
        if MESSAGE_DUMP:
            target = datetime.datetime(year=2017, month=10, day=1)
            if target == m_time:
                with open("message_dump.txt", 'a') as f:
                    f.write(participant + ": " + message.get("content", "") + "\n")

        data[participant][m_time] += len(message.get("content", ""))
        data["total"][m_time] += len(message.get("content", ""))
    return data

def graph_stat_over_time(data, data_type):
    name = "total"
    message_data = data["total"]

    curr_month = datetime.datetime(year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=1)
    if message_data[curr_month]:
        del message_data[curr_month] 
    dates = date2num(list(message_data.keys()))
    counts = np.array(list(message_data.values()))

    dates, counts = zip(*sorted(zip(dates, counts)))


    best_fit_str = "%s best fit" % name

    ### BAR GRAPH ###
    bar = plt.bar(dates, counts, width=20)
    ax = plt.subplot(111)
    ax.xaxis_date()

    ### SCATTER PLOT ###
    ## I think this sucks compared to the bar graph
    # scatter = plt.plot_date(dates, counts, '.', label=name)
    # p1 = np.poly1d(np.polyfit(dates, counts, 10))
    # p1 = np.poly1d(np.polyfit(dates[10:], counts[10:], 30))
    # best_fit = plt.plot_date(dates, p1(dates), '--', label=best_fit_str)
    # plt.autoscale(True)
    # plt.grid(True)
    # plt.ylim(-100)

    plt.legend()
    plt.ylabel('# of %s' % data_type)
    plt.title("%s between %s" % (data_type, " and ".join([i for i in data.keys() if i != "total"])))

def bar_graph(x, y, title, x_axis, y_axis, width=20):
    """Make a bar graph"""
    bar = plt.bar(x, y, width=width)
    ax = plt.subplot(111)
    ax.xaxis_date()
    plt.legend()
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(title)

def most_messaged_by_month():
    res = defaultdict(lambda: ("", 0))

    for person, path in friends.ALL_FRIENDS[:]:
        message_json = get_json(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            name = message_json.get("participants")[0]

            data = characters_over_time(messages)
            message_data = data["total"]

            for date, count in message_data.items():
                if res[date][1] < count:
                    res[date] = (name, count)
    res_list = [[k, v[0], v[1]] for k, v in res.items()]
    res_list.sort()

    res_list = [[str(i[0].year) + "-" + str(i[0].month), i[1], i[2]] for i in res_list] # turn datetime into year-month
    print(tabulate(res_list[:-1], headers=["Month", "Most Messaged Person", "# of messages"]))

def total_messages():
    period = "Year"
    res = defaultdict(int)

    for person, path in friends.ALL_FRIENDS:
        message_json = get_json(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            name = message_json.get("participants")[0]

            data = messages_over_time(messages, period)
            message_data = data[MY_NAME]

            for date, count in message_data.items():
                res[date] += count
    res_list = sorted([(date, count) for date, count in res.items()])
    dates = [elem[0] for elem in res_list[:-1]]
    counts = [elem[1] for elem in res_list[:-1]]
    bar_graph(dates, counts, "Total Messages Sent by %s per %s" % (MY_NAME, period), "", "Total Messages by %s" % period, width=200)

if __name__ == "__main__":
    # group_chat_analysis()
    main(friends.HORACE_HE)
    # most_messaged_by_month()
    # total_messages()
    plt.ion()
    plt.show(block=True)