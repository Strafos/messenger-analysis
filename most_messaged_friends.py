import os

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
    count = 1
    for i in messages_per_friend[:n]:
        print(count, i)
        count += 1
    # with open("a.out", "w") as f:
    #     for friend in friend:

    pprint(messages_per_friend)

most_messaged_friends(20)