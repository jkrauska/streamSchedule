#!/bin/bash

source .venv/bin/activate
export FLASK_APP=main.py  # Set the FLASK_APP environment variable to your main Flask application file
export FLASK_ENV=development  # Set the FLASK_ENV environment variable to development mode
flask run  --host=0.0.0.0
#flask run --reload --host=0.0.0.0
