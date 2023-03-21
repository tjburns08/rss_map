#!/bin/bash

source .venv/bin/activate 
python src/get_rss.py
python src/app.py

