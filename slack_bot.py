import uuid
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from app.event_handler import register_event_handlers
from config.settings import SLACK_BOT_TOKEN
from typing import Any
from app.message_handler import handle_message, initialize_models

# Dictionary to store UUIDs
user_uuid = {}

# Load environment variables
load_dotenv()

# Initialize Slack app
slack_app: App = App(token=SLACK_BOT_TOKEN)

# Register event handlers
register_event_handlers(slack_app)

# Create Flask app
app: Flask = Flask(__name__)
handler: SlackRequestHandler = SlackRequestHandler(slack_app)

# Initialize models
initialize_models()

@app.route("/get_uuid", methods=["POST"])
def generate_id() -> Any:
    event_id = str(uuid.uuid4().hex)
    user_uuid[event_id] = event_id
    print(f"UUID: {user_uuid[event_id]}")
    return jsonify({"status": "success", "uuid": user_uuid[event_id]}), 200

@app.route("/get_prompt", methods=["POST"])
def generate_prompt() -> Any:
    try:
        event = request.json
        if event is None:
            raise ValueError("No JSON payload received")
        
        if 'sdxl' in event:
            response = handle_message(event)
            return jsonify({"status": "success", "response": response}), 200
        
        return jsonify({"status": "error", "message": "Missing sdxl data"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/slack/events", methods=["POST"])
def slack_events() -> Any:
    return handler.handle(request)

@app.route("/receive_message", methods=["POST"])
def receive_message() -> Any:
    """Endpoint to receive and save a message."""
    try:
        event = request.json
        if event is None:
            raise ValueError("No JSON payload received")

        user_id = event.get('user')
        
        if user_id is None or user_id not in user_uuid:
            return jsonify({"status": "error", "message": "uuid error"}), 400

        response = handle_message(event)
        return jsonify({"status": "success", "response": response}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
