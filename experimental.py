from friends import MY_NAME

# Either these don't work or don't say anything useful


def message_freq(messages, participant):
    # After a gap in talking, who initiates first?
    # Obvious problem is conversations can go on hiatus for a couple days
    gaps = [.01, 1, 2, 5, 10]
    tdelta_gaps = [datetime.timedelta(days=i) for i in gaps]

    print("Gap\tZaibo Count\t%s Count\t%s %%\t %s %%" %
          (participant, MY_NAME, participant))
    for gap, gap_in_days in zip(tdelta_gaps, gaps):
        prev_msg_t = datetime_from_mtime(messages[-1]["timestamp_ms"])
        counters = {
            MY_NAME: 0,
            participant: 0  # Other participant. We assume there is only one
        }
        for message in reversed(messages):
            curr_msg_t = datetime_from_mtime(message["timestamp_ms"])
            sender = message["sender_name"]
            t_delta = curr_msg_t - prev_msg_t
            if t_delta > gap:
                counters[sender] += 1
            prev_msg_t = curr_msg_t
        total_count = sum(counters.values()) + 1
        print("%f\t%d\t%d\t%f\t%f" % (gap_in_days,
                                      counters[MY_NAME],
                                      counters[participant],
                                      counters[MY_NAME]/total_count,
                                      counters[participant]/total_count))


def generate_normalization(messages):
    counters = {}
    for message in messages:
        sender = message["sender_name"]
        counters[sender] = 1 if sender not in counters else counters[sender] + 1


def average_spread(paths=friends.ALL_FRIEND_PATHS):
    # Experimental
    paths = paths[:20]
    stats = ["Characters", "Words", "Messages", "Clusters"]
    all_spreads = []
    all_zbo = []
    for path in paths:
        message_json = get_json(path)
        messages = message_json.get("messages", [])
        participant = message_json.get("participants")[0]
        data = get_all_stats(messages)

        spreads = []
        zbo = []
        for small_stat, big_stat in combinations(stats, 2):
            me = friends.MY_NAME
            other = [name for name in data["Characters"]["Month"]
                     if name != "total" and name != friends.MY_NAME][0]
            sender_averages = (
                sum(data[small_stat]["Year"][me].values()) /
                sum(data[big_stat]["Year"][me].values()),
                sum(data[small_stat]["Year"][other].values()) /
                sum(data[big_stat]["Year"][other].values())
            )
            # spread = sender_averages[0]/sender_averages[1]
            zbo.append(sender_averages[0])
            spread = sender_averages[0]-sender_averages[1]
            spreads.append(spread)
        all_spreads.append([other, *spreads])
        all_zbo.append([*zbo])
    inspect = 3
    all_spreads.sort(key=lambda x: x[inspect], reverse=True)
    # print(tabulate(all_spreads, headers=["Name", *["%s per %s" % combo for combo in combinations(stats, 2)]]))
    # bar = plt.hist([x[inspect] for x in all_spreads], 8)

    mean_stdev = []
    combos = ["%s per %s" % x for x in list(combinations(stats, 2))]
    zbo_stats = []
    for i in range(1, 7):
        avg = np.average([x[i] for x in all_spreads])
        stdev = np.std([x[i] for x in all_spreads])
        mean_stdev.append([combos[i-1], avg, stdev])

        avg = np.average([x[i-1] for x in all_zbo])
        stdev = np.std([x[i-1] for x in all_zbo])
        zbo_stats.append([combos[i-1], avg, stdev])
        # print("%s avg: %f\tstdev: %f" % (combos[i-1], avg, stdev))
    print(tabulate(mean_stdev, headers=[
          "Zaibo to other ratio", "Average", "STDEV"]))
    print("==============================================================")
    print(tabulate(zbo_stats, headers=["Zaibo stats", "Average", "STDEV"]))


def average_response_time(message_json):
    # Confounding data: need to know when a conversation ends
    participant = message_json.get("participants")[0]
    messages = message_json.get("messages")
    data = defaultdict(lambda: defaultdict(int))

    first_message = messages[-1]
    prev_msg_t = datetime.datetime.fromtimestamp(first_message["timestamp_ms"])
    prev_sender = first_message["sender_name"]
    for message in reversed(messages):
        curr_msg_t = datetime.datetime.fromtimestamp(message["timestamp_ms"])
        curr_sender = message["sender_name"]
        if curr_sender != prev_sender:
            t_delta = curr_msg_t - prev_msg_t
            data[curr_sender]["response_time"] += t_delta.total_seconds()
            data[curr_sender]["responses"] += 1
        prev_msg_t = curr_msg_t
        prev_sender = curr_sender

    res = []
    for k, v in data.items():
        if k == friends.MY_NAME:
            k = "%s + %s" % (k, participant)
        res.append([k, v["response_time"]//60/v["responses"]])
    return res
    # for k, v in data.items():
    #     print(k, v["response_time"]//60/v["responses"])
