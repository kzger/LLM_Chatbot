import logging
from collections import defaultdict, deque
from typing import Dict, Deque, List, Any
from threading import Lock
from dataclasses import dataclass, field

import requests
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage, ShowLoadingAnimationRequest

from services.llama_service import request_llama_chat
from services.llava_service import request_llava_chat
from services.prompt_service import request_prompt_chat
from app.utils import is_image_file, download_image, image_to_base64
from config.settings import LLAMA_API_URL, LLAVA_API_URL, SLACK_BOT_TOKEN, LINE_CHANNEL_ACCESS_TOKEN
from model.model_list import LLModelList

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User conversation data
user_conversations: Dict[str, Deque[Dict[str, str]]] = defaultdict(lambda: deque(maxlen=10))
user_system_prompts: Dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=1))
user_active_request: Dict[str, bool] = defaultdict(bool)
user_locks: Dict[str, Lock] = defaultdict(Lock)

# LINE Bot configuration
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

def initialize_models():
    logger.info("Initializing models...")
    request_llama_chat(LLAMA_API_URL, LLModelList.ZH_TW_L3_8B, [{"role": "system", "content": "Initialize ZH_TW_L3_8B"}])
    # request_llama_chat(LLAMA_API_URL, LLModelList.LLAMA3_8B, [{"role": "system", "content": "Initialize LLAMA3_8B"}],)
    # request_llava_chat(LLAVA_API_URL, LLModelList.LLAVA, "Initialize LLAVA", [])
    # request_prompt_chat(LLAMA_API_URL, LLModelList.PROMPT, [{"role": "system", "content": "Initialize PROMPT"}],)

def handle_message(handler) -> Any:
    user_id = handler.get_user_id()
    with user_locks[user_id]:
        if user_active_request[user_id]:
            return
        user_active_request[user_id] = True

    try:
        return handler.process_message()
    finally:
        with user_locks[user_id]:
            user_active_request[user_id] = False

@dataclass
class GenericHandler:
    event: Dict[str, Any]

    def get_user_id(self) -> str:
        return str(self.event.get("user"))

    def process_message(self) -> str:
        if "sdxl" in self.event:
            return self.handle_prompt_message()
        return self.handle_text_en_message()

    def handle_special_commands(self) -> str:
        user_id: str = self.get_user_id()
        text: str = str(self.event.get("text"))
        if text.startswith("!"):
            user_system_prompts[user_id].append(text[1:])
            return f"System prompt updated: {text[1:]}"
        elif text.startswith("_"):
            user_conversations[user_id].clear()
            user_system_prompts[user_id].clear()
            return "All records cleared."
        else:
            return "Unknown command."

    def handle_prompt_message(self) -> str:
        user_id: str = self.get_user_id()
        sdxl: str = str(self.event.get("sdxl"))
        user_conversations[user_id].append({"role": "user", "content": sdxl})
        messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[user_id]]
        messages += list(user_conversations[user_id])
        response: str = request_prompt_chat(LLAMA_API_URL, LLModelList.PROMPT, messages)
        if response:
            user_conversations[user_id].append({"role": "assistant", "content": response})
        return response

    def handle_text_en_message(self) -> str:
        user_id: str = self.get_user_id()
        text: str = str(self.event.get("text"))
        user_conversations[user_id].append({"role": "user", "content": text})
        messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[user_id]]
        messages += list(user_conversations[user_id])
        response: str = request_llama_chat(LLAMA_API_URL, LLModelList.LLAMA3_8B, messages)
        if response:
            user_conversations[user_id].append({"role": "assistant", "content": response})
        return response

    def reply_message(self, response_text: str) -> Any:
        raise NotImplementedError

@dataclass
class SlackHandler(GenericHandler):

    def process_message(self) -> str:
        if "files" in self.event:
            return self.handle_image_message()
        return self.handle_text_en_message()

    def handle_image_message(self) -> str:
        text: str = str(self.event.get("text", ""))
        response: str = ""
        for file in self.event.get("files", []):
            if is_image_file(file):
                image_content = download_image(file["url_private"], SLACK_BOT_TOKEN)
                if image_content:
                    base64_image: str = image_to_base64(image_content)
                    response += request_llava_chat(LLAVA_API_URL, LLModelList.LLAVA, text, [base64_image])
        return response

@dataclass
class LineHandler(GenericHandler):
    user_id: str = field(init=False)
    message_type: str = field(init=False)
    text: str = field(init=False, default="")
    source_type: str = field(init=False)
    reply_token: str = field(init=False)
    quote_token: str = field(init=False, default="")

    def __post_init__(self):
        self.user_id = self.event["source"]["userId"]
        self.message_type = self.event["message"]["type"]
        self.text = self.event["message"].get("text", "")
        self.source_type = self.event["source"]["type"]
        self.reply_token = self.event["replyToken"]
        self.quote_token = self.event["message"].get("quoteToken", "")

    def get_user_id(self) -> str:
        return self.user_id

    def process_message(self) -> str:
        if self.source_type == "user":
            self.show_loading_animation(self.user_id, 60)
            if self.text.startswith("!") or self.text.startswith("_"):
                response = self.handle_special_commands()
            else:
                if self.message_type == "image":
                    response = self.handle_image_message()
                else:
                    response = self.handle_text_tw_message()
        elif self.source_type in ["group", "room"]:
            if not (self.text.startswith("!") or self.text.startswith("_") or self.text.startswith("?")):
                return "Ignored non-special command message in group/room."
            response = self.handle_special_commands()
        else:
            response = self.handle_text_tw_message()

        return self.reply_message(response)

    def show_loading_animation(self, chat_id: str, loading_seconds: int):
        url = "https://api.line.me/v2/bot/chat/loading/start"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        data = ShowLoadingAnimationRequest(chatId=chat_id, loadingSeconds=loading_seconds).to_json()
        response = requests.post(url, headers=headers, data=data)
        return response.json()

    def handle_special_commands(self) -> str:
        if self.text.startswith("!"):
            user_system_prompts[self.user_id].append(self.text[1:])
            return f"System prompt updated: {self.text[1:]}"
        elif self.text.startswith("_"):
            user_conversations[self.user_id].clear()
            user_system_prompts[self.user_id].clear()
            return "All records cleared."
        elif self.text.startswith("?"):
            self.text = self.text[1:]
            return self.handle_text_tw_message()
        else:
            return "Unknown command."

    def handle_text_tw_message(self) -> str:
        user_conversations[self.user_id].append({"role": "user", "content": self.text})
        messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[self.user_id]]
        messages += list(user_conversations[self.user_id])
        response: str = request_llama_chat(LLAMA_API_URL, LLModelList.ZH_TW_L3_8B, messages)
        if response:
            user_conversations[self.user_id].append({"role": "assistant", "content": response})
        return response

    def handle_image_message(self) -> str:
        message_id: str = self.event["message"]["id"]
        image_content = download_image(self.get_line_image_url(message_id), LINE_CHANNEL_ACCESS_TOKEN)
        if not image_content:
            return "Failed to download image."
        base64_image: str = image_to_base64(image_content)
        response = request_llava_chat(LLAVA_API_URL, LLModelList.LLAVA, self.text, [base64_image])
        return response

    def get_line_image_url(self, message_id: str) -> str:
        url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        headers = {
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            return url
        return ""

    def reply_message(self, response_text: str) -> Any:
        reply_message = TextMessage(
            quickReply=None,
            sender=None,
            text=response_text,
            emojis=None,
            quoteToken=self.quote_token,
        )
        reply_request = ReplyMessageRequest(
            replyToken=self.reply_token,
            messages=[reply_message],
            notificationDisabled=False,
        )

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(reply_request)
