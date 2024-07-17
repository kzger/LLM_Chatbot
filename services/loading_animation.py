import time
from threading import Thread
from slack_bolt import App
from slack_bolt.context.say import Say
from typing import List

loading_frames: List[str] = [":hourglass_flowing_sand:", ":hourglass:"]
stop_loading: bool = False

def start_loading_animation(app: App, say: Say, channel: str) -> str:
    ts: str = say(text=loading_frames[0], channel=channel)["ts"]
    thread: Thread = Thread(target=show_loading_animation, args=(app, channel, ts))
    thread.start()
    return ts

def show_loading_animation(app: App, channel: str, ts: str) -> None:
    frame_index: int = 0
    while not stop_loading:
        app.client.chat_update(channel=channel, ts=ts, text=loading_frames[frame_index])
        frame_index = (frame_index + 1) % len(loading_frames)
        time.sleep(1)
            
def stop_loading_animation(app: App, channel: str, ts: str, final_text: str) -> None:
    global stop_loading
    stop_loading = True
    app.client.chat_update(channel=channel, ts=ts, text=final_text)
