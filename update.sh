#!/bin/bash

source .venv/bin/activate 
python src/get_rss_opml.py
python src/process_data.py
python src/app.py
