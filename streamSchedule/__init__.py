import json
from flask import Flask


def create_app():
    app = Flask(__name__)


    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config["SCHEDULER_API_ENABLED"] = True


    return app