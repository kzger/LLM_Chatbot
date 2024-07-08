import os
from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from app.event_handler import register_event_handlers
from config.settings import SLACK_BOT_TOKEN, LLAMA_API_URL, LLAVA_API_URL
from typing import Any

# Load environment variables
load_dotenv()

# Initialize Slack app
slack_app: App = App(token=SLACK_BOT_TOKEN)

# Register event handlers
register_event_handlers(slack_app)

# Create Flask app
app: Flask = Flask(__name__)
handler: SlackRequestHandler = SlackRequestHandler(slack_app)

@app.route("/slack/events", methods=["POST"])
def slack_events() -> Any:
    return handler.handle(request)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
