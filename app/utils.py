import requests
import base64
from typing import Dict, Any, Optional

def is_image_file(file: Dict[str, Any]) -> bool:
    """Check if the given file is an image based on its MIME type."""
    return file['mimetype'].startswith('image/')

def download_image(url: str, token: str) -> Optional[bytes]:
    """Download an image from the given URL using the provided authentication token."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    return None

def image_to_base64(image_content: bytes) -> str:
    """Convert image content to a base64 encoded string."""
    return base64.b64encode(image_content).decode('utf-8')
