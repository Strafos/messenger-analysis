import os
import datetime
from pprint import pprint
from tabulate import tabulate
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num

import friends
from helpers import get_json, check_participants, bucket_datetime

def main(paths=[]):
    for path in paths:
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
            data = get_all_stats(messages)
    graph_stat(data, stat="Characters", period="Day", name="total")
    graph_stat(data, stat="Characters", period="Month", name="Horace He")

def datetime_from_mtime(mtime):
    return datetime.datetime.fromtimestamp(mtime)

def get_all_stats(messages):
    """
    Given 1 on 1 messages, generate stats over periods

    Supported stats:
    "Characters": total characters
    "Messages": total times enter is pressed
    "Clusters": all messages sent before being interupted by other participant is one cluster

    the core data structure is:
    {
        "name1": {
            datetime.datetime: stat_val1
        },
        "name2": {
            datetime.datetime: stat_val2
        },
        "total": {
            datetime.datetime: stat_val1+stat_val2
        },
    }

    data is a four layer dictionary which returns 
    a "core data structure" given a Stat and Period key
    Ex: data["messages"]["Day"] gives daily total message statistic
    """
    periods = ["Year", "Month", "Day"]
    stats = ["Characters", "Messages", "Clusters"]

    # Create a four-layered defaultdict with default int leaf
    # Stat -> Period -> name -> datetime.datetime -> value
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    prev_sender = None
    for message in reversed(messages):
        timestamp = datetime_from_mtime(message["timestamp"])
        sender_name = message["sender_name"]
        content = message.get("content", "")

        for period in periods:
            m_time = bucket_datetime(timestamp, period)

            # Aggregate for messages, characters, and clusters
            for name in [sender_name, "total"]:
                data["Messages"][period][name][m_time] += 1
                data["Characters"][period][name][m_time] += len(content)
                if sender_name != prev_sender:
                    data["Clusters"][period][name][m_time] += 1
            
        prev_sender = sender_name
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

def graph_stat(data, stat="Messages", period="Month", name="total"):
    """
    Graph data from get_all_stats
    """

    # Parse data and sort by dates
    message_data = data[stat][period][name]
    dates = date2num(list(message_data.keys()))
    counts = np.array(list(message_data.values()))
    dates, counts = zip(*sorted(zip(dates, counts)))

    ### BAR GRAPH ###
    bar = plt.bar(dates, counts, width=20)
    ax = plt.subplot(111)
    ax.xaxis_date()

    ### SCATTER PLOT ###
    # I think the bar graph displays data better
    # scatter = plt.plot_date(dates, counts, '.', label=name)
    # p1 = np.poly1d(np.polyfit(dates, counts, 10))
    # best_fit_str = "%s best fit" % name
    # best_fit = plt.plot_date(dates, p1(dates), '--', label=best_fit_str)
    # plt.autoscale(True)
    # plt.grid(True)
    # plt.ylim(-100)
    # plt.legend()

    plt.ylabel('# of %s' % stat)
    plt.title("%s between %s" % (stat, " and ".join([i for i in data[stat][period].keys() if i != "total"])))

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

def total_messages_sent(name, period="Year"):
    """
    Graph all messages sent by YOU
    """
    res = defaultdict(int)

    for person, path in friends.ALL_FRIENDS:
        message_json = get_json(path)
        if check_participants(message_json):
            messages = message_json.get("messages", [])
            name = message_json.get("participants")[0]

            data = messages_over_time(messages, period)
            message_data = data[friends.MY_NAME]

            for date, count in message_data.items():
                res[date] += count
    res_list = sorted([(date, count) for date, count in res.items()])
    dates = [elem[0] for elem in res_list[:-1]]
    counts = [elem[1] for elem in res_list[:-1]]
    bar_graph(dates, counts, "Total Messages Sent by %s per %s" % (friends.MY_NAME, period), "", "Total Messages by %s" % period, width=200)

if __name__ == "__main__":
    main([friends.HORACE_HE])
    # group_chat_analysis()
    # most_messaged_by_month()
    # total_messages()
    plt.ion()
    plt.show(block=True)

# TODO
# longest dry spell
# average message length
# "enters" per response
# Average response time