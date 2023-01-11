#!/bin/bash

source .venv/bin/activate 
pip install -r requirements.txt
cd src 
python scrape_tweets.py

# TODO figure out why this isn't updating by virtue of just running this
# cd ../notebooks
# jupyter nbconvert --to html --no-input biorxiv_medrxiv_history.ipynb

# Warning: make sure that the directory is correct
# cp biorxiv_medrxiv_history.html ../../tyler_burns_website/public/biorxiv_medrxiv_history.html
