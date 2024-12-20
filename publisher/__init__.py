from flask import Flask
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import os

def create_app():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Initialize Flask app
    flask_app = Flask(__name__)

    # Initialize Slack Bolt app
    slack_app = App(
        token=os.getenv("SLACK_BOT_TOKEN"),
        signing_secret=os.getenv("SLACK_SIGNING_SECRET")
    )
    handler = SlackRequestHandler(slack_app)

    return flask_app, slack_app, handler
