import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN: str = str(os.getenv("SLACK_BOT_TOKEN"))
LLAMA_API_URL: str = str(os.getenv("LLAMA_API_URL"))
LLAVA_API_URL: str = str(os.getenv("LLAVA_API_URL"))
LINE_CHANNEL_ACCESS_TOKEN: str = str(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
LINE_CHANNEL_SECRET: str = str(os.getenv("LINE_CHANNEL_SECRET"))
