
## Introduction
This project takes RSS feeds as input, and converts the titles into [sBERT embeddings](https://arxiv.org/abs/1908.10084). These are then reduced to 2 dimensions using UMAP. This is viewed as an interactive map, allowing the user to browse the map, or view the feed as a standard list.

For context, I have done a similar thing with Twitter, but as of May 2023, it's getting more complicated to do this.

## How to use
1. Clone the repo.
2. Run `pip install -r requirements.txt`
3. Run `./update.sh`
4. In the command line, you'll see the message "Dash is running on http://xxx.x.x.x:xxxx/". Go to that address in your browser of choice.

## Extensions in the near future
Right now I just have a fixed set of RSS feeds, but I'm going to ultimately give the user the ability to upload their feeds.
