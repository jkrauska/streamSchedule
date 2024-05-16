#!/bin/bash
set -e

# Needed before uwsgi
sudo apt-get install libssl-dev
sudo apt-get install libpcre3 libpcre3-dev


[ ! -d ".venv" ] && python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
