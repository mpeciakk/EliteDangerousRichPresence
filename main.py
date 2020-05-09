from rpc import RPClient
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from config import LOGS_PATH
import asyncio

def start_client():
    print("New game logs detected, launching RichPresence...")

    client = RPClient()
    client.start()

async def start_watcher():
    event_handler = PatternMatchingEventHandler("*", "", False, False)

    def on_created(event):
        start_client()

    event_handler.on_created = on_created

    observer = Observer()
    observer.schedule(event_handler, LOGS_PATH, recursive=True)
    observer.start()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_watcher())
