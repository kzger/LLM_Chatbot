from collections import defaultdict, deque
from typing import Dict, Deque, List, Any
from services.llama_service import request_llama_chat
from services.llava_service import request_llava_chat
from services.prompt_service import request_prompt_chat
from app.utils import is_image_file, download_image, image_to_base64
from config.settings import LLAMA_API_URL, LLAVA_API_URL, SLACK_BOT_TOKEN
from model.model_list import LLModelList

# Initialize data structures
user_conversations: Dict[str, Deque[Dict[str, str]]] = defaultdict(lambda: deque(maxlen=10))
user_system_prompts: Dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=1))


# Initialize models
def initialize_models():
    print("Initializing models...")
    request_llama_chat(LLAMA_API_URL, LLModelList.ZH_TW_L3_8B, [{"role": "system", "content": "Initialize ZH_TW_L3_8B"}],)
    request_llama_chat(LLAMA_API_URL, LLModelList.LLAMA3_8B, [{"role": "system", "content": "Initialize LLAMA3_8B"}],)
    request_llava_chat(LLAVA_API_URL, LLModelList.LLAVA, "Initialize LLAVA", [])
    request_prompt_chat(LLAMA_API_URL, LLModelList.PROMPT, [{"role": "system", "content": "Initialize PROMPT"}],)


def handle_message(event: Dict[str, Any]) -> str:
    """Handle message based on event type."""
    text: str = str(event.get("text", ""))
    if text.startswith("!") or text.startswith("_") or text.startswith("?"):
        return handle_special_commands(event)
    elif "files" in event:
        return handle_image_message(event)
    elif "sdxl" in event:
        return handle_prompt_message(event)
    else:
        return handle_text_message(event)


def handle_special_commands(event: Dict[str, Any]) -> str:
    user_id: str = str(event.get("user"))
    text: str = str(event.get("text", ""))

    if text.startswith("!"):
        user_system_prompts[user_id].append(text[1:])
        return f"System prompt updated: {text[1:]}"
    elif text.startswith("_"):
        user_conversations[user_id].clear()
        user_system_prompts[user_id].clear()
        return "All records cleared."
    elif text.startswith("?"):
        return handle_question_message(user_id, text)
    else:
        return "Unknown command."


def handle_question_message(user_id: str, text: str) -> str:
    """Handle messages starting with '?'."""
    user_conversations[user_id].append({"role": "user", "content": text})
    messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[user_id]]
    messages += list(user_conversations[user_id])

    response: str = request_llama_chat(LLAMA_API_URL, LLModelList.ZH_TW_L3_8B, messages)
    if response:
        user_conversations[user_id].append({"role": "assistant", "content": response})
    return response


def handle_image_message(event: Dict[str, Any]) -> str:
    text: str = str(event.get("text", ""))
    response: str = ""
    for file in event.get("files", []):
        if is_image_file(file):
            image_content = download_image(file["url_private"], SLACK_BOT_TOKEN)
            if image_content:
                base64_image: str = image_to_base64(image_content)
                response += request_llava_chat(LLAVA_API_URL, LLModelList.LLAVA, text, [base64_image])
    return response


def handle_text_message(event: Dict[str, Any]) -> str:
    user_id: str = str(event.get("user"))
    text: str = str(event.get("text", ""))
    user_conversations[user_id].append({"role": "user", "content": text})
    messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[user_id]]
    messages += list(user_conversations[user_id])

    response: str = request_llama_chat(LLAMA_API_URL, LLModelList.LLAMA3_8B, messages)
    if response:
        user_conversations[user_id].append({"role": "assistant", "content": response})
    return response


def handle_prompt_message(event: Dict[str, Any]) -> str:
    sdxl_event_data = event.get("sdxl")
    if not sdxl_event_data:
        return "SDXL event data is missing."

    user_id = str(event.get("user", ""))
    messages: List[Dict[str, str]] = [{"role": "system", "content": prompt} for prompt in user_system_prompts[user_id]]
    messages.append({"role": "user", "content": sdxl_event_data})

    response: str = request_prompt_chat(LLAMA_API_URL, LLModelList.PROMPT, messages)
    if response:
        user_conversations[user_id].append({"role": "assistant", "content": response})
    return response
