import json
import datetime

def get_json(path):
    with open(path, "r") as f:
        return json.loads(f.read())

def check_participants(message_json):
    """To check 1 on 1 messages"""
    return len(message_json.get("participants", [])) == 1

def bucket_datetime(timestamp, period="Month"):
    """
    We aggregate data such as message count by casting them to a datetime bucket

    For example, if we want data by month, an event happens on August 5th, 1998
    will be cast to the August-1998 bucket which allows use to treat all events
    on August 1998 the same
    """
    if period == "Day":
        return datetime.datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day)
    elif period == "Month":
        return datetime.datetime(year=timestamp.year, month=timestamp.month, day=1)
    elif period == "Year":
        return datetime.datetime(year=timestamp.year, month=1, day=1)
    else:
        raise Exception("Unsupported period: %s", period)