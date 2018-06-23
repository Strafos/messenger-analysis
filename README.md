# Facebook Message Analysis

Analyze Facebook messages for interesting statistics

### Prerequisites

```
python3 and these libraries:
pip install matplotlib # matplotlib
pip install numpy      # numpy
pip install tabulate   # tabulate
```

### Getting Started
Clone the repo
```
git clone https://github.com/Strafos/fb_messenger_analysis
```
Follow instructions [here](https://www.facebook.com/help/1701730696756992?helpref=hc_global_nav) to download your Facebook message data.

Make sure to select "JSON" for format. The quality doesn't matter since we are only looking at texts.

After Facebook processes the request (could take up to a couple hours), unzip the data

### Setup

`setup.py` will generate `friends.py` which contains pains to relevant message dumps.

Before running, edit `setup.py`:
1. Change `BASE_DIR` to be the path of your unzipped message dump
2. Change `MY_NAME` to your own name in the format "John Smith"

### Examples