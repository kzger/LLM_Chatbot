import requests
import json
from typing import List, Optional, Dict, Any

def request_llava_chat(url: str, model: str, prompt: str, images: List[str]) -> str:
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "images": images,
        "stream": False,
        "keep_alive": -1,
    }
    response = requests.post(url, json=payload)
    response_dict = json.loads(response.text)
    response_content = response_dict.get('response')
    return str(response_content) if response_content else "Error in response"
