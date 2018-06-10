import os
import datetime
from pprint import pprint
from tabulate import tabulate
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num

import friends
from helpers import get_json, bucket_datetime, time_format, width_dict

def main(paths=[]):
    for path in paths:
        message_json = get_json(path)
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
        graph_stat(data, stat="Clusters", period="Month", name="total")

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

def message_dump(messages):
    """
    Dump messages from a specific time
    """
    for message in messages:
        participant = message["sender_name"]

        # Grab timestamp from message and cast it to a month + year timestamp
        timestamp = datetime_from_mtime(message["timestamp"])
        m_time = datetime.datetime(year=timestamp.year, month=timestamp.month, day=1)

        # We use this to get all messages from a certain month
        target = datetime.datetime(year=2017, month=10, day=1)
        if target == m_time:
            with open("message_dump.txt", 'a') as f:
                f.write(participant + ": " + message.get("content", "") + "\n")

        data[participant][m_time] += len(message.get("content", ""))
        data["total"][m_time] += len(message.get("content", ""))
    return data

def graph_stat(data, stat="Messages", period="Month", name="total", message_data=None):
    """
    Graph data from get_all_stats
    """

    # Parse data and sort by dates
    if not message_data:
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
    plt.title("%s between %s per %s" % (stat, " and ".join([i for i in data[stat][period].keys() if i != "total"]), period))

def top_stat(stat="Messages", period="Month"):
    """
    Print top messaged person per period in a table
    """
    res = defaultdict(lambda: ("", 0))

    for person, path in friends.ALL_FRIENDS:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        name = message_json.get("participants")[0]

        message_data = get_all_stats(messages)[stat][period]["total"]

        for date, count in message_data.items():
            if res[date][1] < count:
                res[date] = (name, count)
    
    # We want to sort by date
    res_list = sorted([[date, name, count] for date, (name, count) in res.items()])

    res_list = [[date.strftime(time_format(period)), name, count] for date, name, count in res_list]
    print(tabulate(res_list, headers=[period, "Most %s" % stat, "Count"]))

def top_n_stat(n, stat="Messages", period="Month"):
    """
    Print top n messaged person per period in a table
    """
    res = defaultdict(list)

    for person, path in friends.ALL_FRIENDS:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        name = message_json.get("participants")[0]

        message_data = get_all_stats(messages)[stat][period]["total"]

        for date, count in message_data.items():
            res[date].append((name, count))
    
    # We want to sort by date
    res_list = sorted([[date, count_list] for date, count_list in res.items()])

    # Sorry...
    res_list = [[date.strftime(time_format(period)), *sorted(count_list, key=lambda x: x[1], reverse=True)[:n]] for date, count_list in res_list]
    print(tabulate(res_list, headers=[period, *[str(i) for i in range(1, n+1)]]))

def total_stat_sent(stat="Messages", period="Year"):
    """
    Graph all of a stat sent by YOU
    Must setup MY_NAME in friends.py
    """
    res = defaultdict(int)

    for person, path in friends.ALL_FRIENDS:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        name = message_json.get("participants")[0]

        data = get_all_stats(messages)
        message_data = data[stat][period][friends.MY_NAME]

        for date, count in message_data.items():
            res[date] += count

    res_list = sorted([(date, count) for date, count in res.items()])
    dates = [elem[0] for elem in res_list[:-1]]
    counts = [elem[1] for elem in res_list[:-1]]

    bar = plt.bar(dates, counts, width=width_dict[period])
    ax = plt.subplot(111)
    ax.xaxis_date()
    plt.ylabel('# of %s' % stat)
    plt.title("Total %s Sent per %s" % (stat, period))

if __name__ == "__main__":
    # top_stat(stat="Characters", period="Month")
    top_n_stat(5, stat="Characters", period="Year")
    # main([friends.RISHI_TRIPATHY])
    # total_stat_sent(period="Year")
    plt.show(block=True)

# TODO
# longest dry spell
# average message length
# "enters" per response
# Average response time