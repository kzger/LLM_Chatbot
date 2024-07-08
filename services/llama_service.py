import requests
import json
from typing import List, Optional, Dict, Any

def request_llama_chat(url: str, model: str, messages: List[Dict[str, str]]) -> str:
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
    }
    response = requests.post(url, json=payload)
    response_dict = json.loads(response.text)
    response_content = response_dict.get('message', {}).get('content')
    return str(response_content) if response_content else "Error in response"
