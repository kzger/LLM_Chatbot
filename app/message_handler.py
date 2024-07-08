from collections import defaultdict, deque
from typing import Dict, Deque, List, Any, Optional
from services.llama_service import request_llama_chat
from services.llava_service import request_llava_chat
from app.utils import is_image_file, download_image, image_to_base64
from config.settings import LLAMA_API_URL, LLAVA_API_URL, SLACK_BOT_TOKEN
from model.model_list import LLModelList

user_conversations: Dict[str, Deque[Dict[str, str]]] = defaultdict(lambda: deque(maxlen=10))
user_system_prompts: Dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=1))

def handle_message(event: Dict[str, Any]) -> str:
    user_id: str = str(event.get('user'))
    text: str = str(event.get('text'))
    
    if text.startswith('!'):
        user_system_prompts[user_id].append(text[1:])
        return f"System prompt updated: {text[1:]}"
    elif text.startswith('_'):
        user_conversations[user_id].clear()
        user_system_prompts[user_id].clear()
        return "All records cleared."
    elif 'files' in event:
        return handle_image_message(event, text)
    else:
        return handle_text_message(event, text)

def handle_image_message(event: Dict[str, Any], text: str) -> str:
    response: str = ""
    for file in event['files']:
        if is_image_file(file):
            image_content = download_image(file['url_private'], SLACK_BOT_TOKEN)
            if image_content:
                base64_image: str = image_to_base64(image_content)
                response += request_llava_chat(LLAVA_API_URL, LLModelList.LLAVA, text, [base64_image])
    return response

def handle_text_message(event: Dict[str, Any], text: str) -> str:
    user_id: str = str(event.get('user'))
    user_conversations[user_id].append({"role": "user", "content": text})
    messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[user_id]]
    messages += list(user_conversations[user_id])
    
    response: str = request_llama_chat(LLAMA_API_URL, LLModelList.ZH_TW_L3_8B, messages)
    if response:
        user_conversations[user_id].append({"role": "assistant", "content": response})
    return response
