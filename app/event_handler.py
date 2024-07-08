import logging
from slack_bolt import App
from slack_bolt.context.say import Say
from typing import Dict, Any
from app.message_handler import handle_message
from services.loading_animation import start_loading_animation, stop_loading_animation

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
responsing_list = []

def register_event_handlers(app: App) -> None:
    @app.middleware
    def log_request(logger, body, next) -> Any:
        logger.debug(body)
        return next()

    @app.event("app_mention")
    def event_test(body: Dict[str, Any], say: Say, logger) -> None:
        logger.info(body)
        say("What's up?")

    @app.event("message")
    def handle_event(event: Dict[str, Any], say: Say, ack: Any, logger) -> None:
        logger.info(event)
        ack()
        
        if event.get('subtype') == "message_deleted":
            return
        user_id: Any = event.get('user')
        if user_id in responsing_list:
            return
        responsing_list.append(user_id)
        
        # Start loading animation
        ts: str = start_loading_animation(app, say, event['channel'])
        
        # Handle the message
        response: str = handle_message(event)
        
        # Delete user response info
        if user_id in responsing_list:
            responsing_list.remove(user_id)

        # Stop loading animation and update the message with the response
        stop_loading_animation(app, event['channel'], ts, response)
