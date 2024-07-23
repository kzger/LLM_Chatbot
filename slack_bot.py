import os
import uuid
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from app.event_handler import register_event_handlers
from config.settings import SLACK_BOT_TOKEN, LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from typing import Any
from app.message_handler import handle_message, initialize_models
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store UUIDs
user_uuid = {}

# Initialize Slack app
slack_app = App(token=SLACK_BOT_TOKEN)

# Register event handlers
register_event_handlers(slack_app)

# Slack Request Handler
handler = SlackRequestHandler(slack_app)

# LINE BOT settings
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Ensure models are initialized only once
models_initialized = False

def initialize_app():
    global models_initialized
    if not models_initialized:
        logger.info("Initializing models...")
        initialize_models()
        models_initialized = True

@app.route("/")
def home():
    return "Hi"

@app.route('/ping')
def ping():
    return jsonify({"message": "pong"})

@app.route('/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify(data)

# Slack routes
@app.route("/slack/events", methods=["POST"])
def slack_events() -> Any:
    return handler.handle(request)

# LINE routes
@app.route("/callback", methods=["POST"])
def callback() -> Any:
    if "X-Line-Signature" not in request.headers:
        logger.error("Missing X-Line-Signature header")
        abort(400, "Missing X-Line-Signature header")

    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    logger.debug("Request body: %s", body)  # Use debug level for request body logging

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400, "Invalid signature")
    return "OK"

@line_handler.add(MessageEvent)
def handle_line_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text

        if not user_message.startswith("?"):
            return

        user_id = event.source.user_id
        event_data = {"user": user_id, "text": user_message}

        try:
            response_text = handle_message(event_data)
        except Exception as e:
            logger.error("Error handling message: %s", e)
            response_text = "Error handling message"

        reply_message = TextMessage(
            text=response_text,
            quickReply=None,
            sender=None,
            emojis=None,
            quoteToken=None,
        )
        reply_request = ReplyMessageRequest(
            replyToken=event.reply_token,
            messages=[reply_message],
            notificationDisabled=False,
        )

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(reply_request)

# General routes
@app.route("/get_uuid", methods=["POST"])
def generate_id() -> Any:
    event_id = str(uuid.uuid4().hex)
    user_uuid[event_id] = event_id
    return jsonify({"status": "success", "uuid": user_uuid[event_id]}), 200

@app.route("/get_prompt", methods=["POST"])
def generate_prompt() -> Any:
    try:
        event = request.json
        if event is None:
            raise ValueError("No JSON payload received")

        if "sdxl" in event:
            response = handle_message(event)
            return jsonify({"status": "success", "response": response}), 200

        return jsonify({"status": "error", "message": "Missing sdxl data"}), 400
    except Exception as e:
        logger.error("Error generating prompt: %s", e)
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

        response = handle_message(event)
        return jsonify({"status": "success", "response": response}), 200
    except Exception as e:
        logger.error("Error receiving message: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        initialize_app()  # Ensure models are initialized before starting the server
    app.run(debug=True, host="0.0.0.0", port=5000)
