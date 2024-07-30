import os
import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from app.event_handler import register_event_handlers
from config.settings import SLACK_BOT_TOKEN, LINE_CHANNEL_SECRET
from typing import Any
from app.message_handler import handle_message, initialize_models, LineHandler, GenericHandler
from linebot.v3.webhook import WebhookHandler, InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Dictionary to store user UUIDs
user_uuid = {}

# Initialize Slack Bolt application
slack_app = App(token=SLACK_BOT_TOKEN)

# Register Slack event handlers
register_event_handlers(slack_app)

# Create Slack request handler to integrate with Flask
slack_handler = SlackRequestHandler(slack_app)

# Initialize LINE webhook handler
line_handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Flag to check if models are initialized
models_initialized = False

def initialize_app():
    global models_initialized
    if not models_initialized:
        initialize_models()
        models_initialized = True

@app.route("/get_uuid", methods=["POST"])
def generate_id() -> Any:
    user_id = str(uuid.uuid4().hex)
    user_uuid[user_id] = user_id
    return jsonify({"status": "success", "uuid": user_uuid[user_id]}), 200

@app.route("/get_prompt", methods=["POST"])
def generate_prompt() -> Any:
    try:
        event = request.json
        if event is None:
            raise ValueError("No JSON payload received")

        if "sdxl" in event:
            response = handle_message(GenericHandler(event))
            return jsonify({"status": "success", "response": response}), 200

        return jsonify({"status": "error", "message": "Missing sdxl data"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/receive_message", methods=["POST"])
def receive_message() -> Any:
    try:
        event = request.json
        if event is None:
            raise ValueError("No JSON payload received")

        user_id = event.get("user")

        if user_id is None or user_id not in user_uuid:
            return jsonify({"status": "error", "message": "uuid error"}), 400

        response = handle_message(GenericHandler(event))
        return jsonify({"status": "success", "response": response}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/slack/events", methods=["POST"])
def slack_events() -> Any:
    return slack_handler.handle(request)

@app.route("/callback", methods=["POST"])
def line_callback() -> Any:
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@line_handler.add(MessageEvent, message=(TextMessageContent, ImageMessageContent))
def line_message_handler(event):
    message_data = {
        "source": {"userId": event.source.user_id, "type": event.source.type},
        "message": {"type": event.message.type, "id": event.message.id, "quoteToken": event.message.quote_token},
        "replyToken": event.reply_token
    }

    if isinstance(event.message, TextMessageContent):
        message_data["message"]["text"] = event.message.text
    elif isinstance(event.message, ImageMessageContent):
        message_data["message"]["contentProvider"] = {"type": "line"}

    handler = LineHandler(message_data)
    handle_message(handler)

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        initialize_app()
    app.run(debug=True, host="0.0.0.0", port=5001)
