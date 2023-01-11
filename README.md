
## Introduction
This project scrapes twitter to create a searchable and sortable table of tweets from various users. It is a generalized version my [preprint_history](https://github.com/tjburns08/preprint_history) project.  

This project solves the following problems:
1. How to stay ahead of twitter users and content without endless scrolling.  
2. How to see tweets in the context of the relatively distant past. 

## How to use
1. Clone the repo.
2. Run `pip install -r requirements.txt`
3. Run scrape_tweets.py. Note that the file users.csv contains the twitter users you want to scrape. You can see examples already in the file. This will produce output as csv files that sit in data/.
4. Run tweet_history.ipynb to get the updated table. 
5. To get the html file, run jupyter nbconvert --to html --no-input news_history.ipynb

## Possible extensions
Any twitter username is fair game. It just needs to be added to the users.csv file. Use cases include:
- scientific literature
- news, both mainstream media and independent journalists
- specific people, like Elon Musk

## Acknowledgements
The [snscrape project](https://github.com/JustAnotherArchivist/snscrape), for their amazing work that makes this type of data curation possible. If anything, I hope this project brigs awareness to their work. I also hope that my project contibutes to theirs by providing an example of how to use their python package, which has not been documented yet as their command line interface has. 