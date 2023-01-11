#!/bin/bash

source .venv/bin/activate 
pip install -r requirements.txt
python src/get_rss.py
python src/app.py

