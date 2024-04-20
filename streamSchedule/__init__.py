import json
from flask import Flask


def create_app():
    app = Flask(__name__)

    # Read config from file
    app.config.from_file("secrets.json", load=json.load)

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config["SCHEDULER_API_ENABLED"] = True


    return app