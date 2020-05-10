from presence import PresenceClient
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from config import LOGS_PATH
from asyncio import new_event_loop, set_event_loop
from os import listdir


def start_client():
    loop = new_event_loop()
    set_event_loop(loop)

    print("Game logs detected, launching presence client..")

    client = PresenceClient()
    client.start()


if __name__ == "__main__":
    if len(listdir(LOGS_PATH)) != 0:
        start_client()

    def on_created(event):
        start_client()

    event_handler = PatternMatchingEventHandler("*", "", False, False)
    event_handler.on_created = on_created

    observer = Observer()
    observer.schedule(event_handler, LOGS_PATH, recursive=True)
    observer.start()

    while True:
        sleep(1)
