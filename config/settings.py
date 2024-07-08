import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN: str = str(os.getenv("SLACK_BOT_TOKEN"))
LLAMA_API_URL: str = str(os.getenv("LLAMA_API_URL"))
LLAVA_API_URL: str = str(os.getenv("LLAVA_API_URL"))
