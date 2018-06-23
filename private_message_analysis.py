import os
import datetime
import re
from pprint import pprint
from tabulate import tabulate
from collections import defaultdict
from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num

import friends
from name_hash import NameHasher
from helpers import get_json, bucket_datetime, time_format, width_dict

nh = NameHasher()
ANONYMOUS = True # We can make the data anonymous by hashing all the names except our own

def generate_averages(paths=friends.ALL_FRIEND_PATHS):
    """ Analyze combinations of stats such as "Characters per Words" across all friends in paths"""
    stats = ["Characters", "Words", "Messages", "Clusters"]
    average_stats = []
    for path in paths:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        participant = message_json.get("participants")[0]
        data = get_all_stats(messages)

        for sender in data["Characters"]["Month"]:
            if sender == "total":
                continue
            sender_averages = []
            for small_stat, big_stat in combinations(stats, 2):
                sender_averages.append(
                    sum(data[small_stat]["Year"][sender].values())/sum(data[big_stat]["Year"][sender].values()))
            if sender == friends.MY_NAME:
                if ANONYMOUS:
                    sender = "%s + %s" % (friends.MY_NAME, nh.hash_by_name(participant))
                else:
                    sender = "%s + %s" % (friends.MY_NAME, participant)
            average_stats.append([sender, *sender_averages])
    average_stats.sort(key=lambda x: x[3], reverse=True)

    print(tabulate(average_stats, headers=["Name", *["%s per %s" % combo for combo in combinations(stats, 2)]]))

def get_all_stats(messages):
    """
    Given 1 on 1 messages, generate stats over periods

    Supported stats:
    "Characters": total characters
    "Messages": total times enter is pressed
    "Clusters": all messages sent before being interupted by other participant is one cluster
    "Words": Naively defined as length of space separated message

    data is a four layer dictionary
    Stat -> Period -> name -> datetime.datetime -> value
    data returns a "core data structure" given a Stat and Period key:
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
    Ex: data["Messages"]["Day"] gives daily total message statistic
    """
    periods = ["Year", "Month", "Day"]
    stats = ["Characters", "Messages", "Clusters", "Words"]

    # Create a four-layered defaultdict with default int leaf
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    prev_sender = None
    for message in reversed(messages):
        timestamp = datetime.datetime.fromtimestamp(message["timestamp"])
        sender_name = message["sender_name"]
        if ANONYMOUS and sender_name != friends.MY_NAME:
            sender_name = nh.hash_by_name(sender_name)
        content = message.get("content", "")

        for period in periods:
            m_time = bucket_datetime(timestamp, period)

            # Aggregate for messages, characters, clusters, words
            for name in [sender_name, "total"]:
                data["Characters"][period][name][m_time] += len(content)
                data["Words"][period][name][m_time] += len([i for i in content.split(" ") if ".com" not in i])
                # data["Words"][period][name][m_time] += len(content.split(" "))
                data["Messages"][period][name][m_time] += 1
                if sender_name != prev_sender:
                    data["Clusters"][period][name][m_time] += 1

        prev_sender = sender_name
    return data

def graph_stat(data, stat="Messages", period="Month", name="total", message_data=None):
    """
    Graph parameterized stat from get_all_stats
    """

    # Parse data and sort by dates
    if not message_data:
        message_data = data[stat][period][name]
    dates = date2num(list(message_data.keys()))
    counts = np.array(list(message_data.values()))
    dates, counts = zip(*sorted(zip(dates, counts)))

    ### BAR GRAPH ###
    bar = plt.bar(dates, counts, width=width_dict[period])
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

def top_n_stat(n, stat="Messages", period="Month", show_counts=False):
    """
    Print top n messaged person per period in a table
    """
    res = defaultdict(list)

    for person, path in friends.ALL_FRIENDS:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        name = message_json.get("participants")[0]

        if ANONYMOUS:
            name = nh.hash_by_name(name)

        message_data = get_all_stats(messages)[stat][period]["total"]

        for date, count in message_data.items():
            res[date].append((name, count))
    
    # We want to sort by date
    res_list = sorted([[date, count_list] for date, count_list in res.items()])

    table_data = []
    for date, count_list in res_list[-20:]:
        date_str = date.strftime(time_format(period))                     # Format date by period
        count_list.sort(key=lambda x: x[1], reverse=True)                 # Sort by count
        count_list = count_list[:n]                                       # Truncate to top n
        if show_counts:
            name_and_counts = []
            for name, count in count_list:
                spaces = 30 - len(name) - len(str(count))
                spaces_str = " "*spaces
                s = spaces_str.join([name, str(count)])
                name_and_counts.append(s)
            table_data.append([date_str, *name_and_counts])
        else:
            table_data.append([date_str, *[name for name, count in count_list]])
    print("Top %d Most %s per %s" % (n, stat, period))
    print(tabulate(table_data, headers=[period, *["#%d" % i for i in range(1, n+1)]]))

    # Attempt to use matplotlib for tables... ASCII seems better
    # fig, ax = plt.subplots() 
    # fig.patch.set_visible(False)
    # ax.axis('off')
    # ax.axis('tight')
    # col_labels = ["Month", *["#%d" % i for i in range(1, n+1)]]
    # table = plt.table(cellText=table_data, colWidths=[0.1] * (n+1), loc='center', colLabels=col_labels)

    # # Center the month column
    # cells = table.properties()["celld"]
    # for i in range(len(cells)//(n+1)):
    #     cells[i, 0]._loc = 'center'
    # # Format table
    # table.set_fontsize(24)
    # table.scale(1.3, 1.1)

    # plt.title("Top %d %s Sent by per %s" % (n, stat, period))


def total_stat_sent(stat="Messages", period="Year"):
    """
    Graph all of a stat sent by YOU
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
    plt.title("Total %s Sent %s per %s" % (stat, friends.MY_NAME, period))

def count_specific_word(messages):
    """
    Should we normalization by message count per year?
    """
    words = ["lol", "lool", "loool", "lmao", "haha", "hahaha", "hahahaha"]
    counters = defaultdict(lambda: defaultdict(int))
    for keyword in words:
        for message in messages:
            sender = message["sender_name"]
            if ANONYMOUS and sender != friends.MY_NAME:
                sender = nh.hash_by_name(sender)
            content = message.get("content", "")
            count = content.lower().count(keyword)
            counters[keyword][sender] += count
    table = []
    for keyword, participants in counters.items():
        table.append([keyword, *participants.values()])
    print(tabulate(table, headers=["Word", *participants.keys()]))

def count_links(paths):
    table = []
    link_re = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    for path in paths:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        participant = message_json.get("participants")[0]
        counters = defaultdict(int)

        for message in messages:
            sender = message["sender_name"]
            content = message.get("content", "")
            num_links = len(re.findall(link_re, content))
            counters[sender] += num_links

        table.append([
            participant, 
            counters[friends.MY_NAME]/counters[participant], 
            counters[friends.MY_NAME], 
            counters[participant]])
    table.sort(key=lambda x: x[1], reverse=True)

    if ANONYMOUS:
        for row in table:
            row[0] = nh.hash_by_name(row[0])

    print(tabulate(table, headers=["Name", "Ratio of Links", "Sent by me", "Sent by other"]))
    avg = np.average([x[1] for x in table if x[2] > 50])
    stdev = np.std([x[1] for x in table])
    print("Average Ratio: %f" % avg)
    print("Ratio STDEV: %F" % stdev)

def main(paths=[]):
    for path in paths:
        message_json = get_json(path)
        messages = message_json.get("messages", [])

        data = get_all_stats(messages)
        # graph_stat(data, stat="Messages", period="Year", name="total")

        # count_specific_word(messages)

if __name__ == "__main__":
    """
    supported periods: "Month", "Year", "Day"
    supported stats: "Characters", "Words", Messages", "Clusters"
    """
    # top_n_stat(4, stat="Characters", period="Month", show_counts=True)
    # main(friends.ALL_FRIEND_PATHS[:20])
    # count_links(friends.ALL_FRIEND_PATHS[:20])
    # main([friends.JAIDEV_PHADKE])
    # generate_averages(friends.ALL_FRIEND_PATHS)
    total_stat_sent(stat="Characters", period="Year")

    plt.show(block=True)