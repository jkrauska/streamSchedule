#!/bin/bash
set -e

[ ! -d ".venv" ] && python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
