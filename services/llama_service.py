import requests
import json
from typing import List, Dict, Any

def request_llama_chat(url: str, model: str, messages: List[Dict[str, str]]) -> str:
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_dict = response.json()
        response_content = response_dict.get('message', {}).get('content')
        return str(response_content) if response_content else "No content in response"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except json.JSONDecodeError:
        return "Invalid JSON response"
    except KeyError:
        return "Unexpected response structure"
