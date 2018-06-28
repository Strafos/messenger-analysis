# Facebook Message Analysis

Analyze Facebook messages for interesting statistics

## Prerequisites

```
python3 and these libraries:
pip install matplotlib # matplotlib
pip install numpy      # numpy
pip install tabulate   # tabulate
```

## Getting Started
Clone the repo
```
git clone https://github.com/Strafos/fb_messenger_analysis
```
Follow instructions [here](https://www.facebook.com/help/1701730696756992?helpref=hc_global_nav) to download your Facebook message data.

Make sure to select "JSON" for format. The quality doesn't matter since we are only looking at texts.

After Facebook processes the request (could take up to a couple hours), unzip the data and put it in the repository

## Setup

`setup.py` will generate `friends.py` which contains paths to relevant message dumps.

`setup.py` requires two arguments: 

`--dir`, the directory which has the unzipped facebook message data and

`--name`, which should be your Facebook name in the format "John Smith"

My setup looks like this

```
python setup.py --dir data --name "Zaibo Wang"
```

because my message data directory is in my repository

`friends.py` will list out the top 50 (by default) most messaged friends in order.

## Examples

### Private messages

`private_message_analysis.py` analyzes 1 on 1 messages. All methods are in the main method and commented out by default. Generally, four statistics are supported:

* Characters: total characters
* Messages: total times enter is pressed
* Clusters: all messages sent before being interupted by other participant
* Words: count of elements split by spaces

The supported time periods are Year, Month, Day

All friends were initialized in `friends.py`. To access a friend in `private_message_analysis.py`, use the variable `friends.JOHN_SMITH`

I used a name hash in the following example outputs so they don't use friends' real names

---
`graph_stat` will create a bar graph of a given stat over a period. Default graphs Messages per Year between you and your best friend (most messaged friend).

![graph_messages](https://i.imgur.com/B6yaCSU.png)
![graph_characters](https://i.imgur.com/Qo9s2TY.png)
--- 
`n_top_stat` shows the top n people of a certain stat by the period. By default, it is set to the top 4 characters per month (I think this statistic is the most interesting)

![n_top_stat](https://i.imgur.com/YHSfP6I.png)
---
`count_links` gives an absolute count and ratio of links sent to/received from a person. By default, it only calculates this for the top 20 most messaged friends (I find that after 20, there are few links and the data is not useful)

![count_links](https://i.imgur.com/nzQvhG4.png)

---
`generate_averages` takes combinations of aforementioned stats (such as Characters per Message) and calculates the average per person over all (top 50) friends. 

![generate_averages](https://i.imgur.com/NJ2OPnt.png)

---

`count_specific_words` takes an array of words and a friend to compare word frequency.

![count_specific_words](https://i.imgur.com/NoZHPsQ.png)
---
`total_stat_sent` shows how many of a certain stat you have sent over a period. Default is total Characters per Year.

![total_stat_send](https://i.imgur.com/vt9MYvF.png)

### Group Messages
`group_message_analysis.py` has the code to analyze group messages. It is a little tricker to set up. The easiest way to run is to pass a path to a group message.json to the main method in `group_message_analysis.py`.

I found some difficulty in finding group messages within my message dump so another way to do it is to use `find_groupchat()` in `setup.py`. This lets me specify a condition such as all groupchats with more than 15 participants. Then I add them to the GROUPCHAT variable in `setup.py` which will generate groupchats in `friends.py`. Then, these paths can be passed into the main method by `friends.${chat_name}`.

Result:
![group_chat](https://i.imgur.com/xzLZC60.png)