import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("staging_folder", help="Path to staging folder in mysimbdp")
args = parser.parse_args()

watch_dir = args.staging_folder


class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"{event.src_path} has been created")


event_handler = MyEventHandler()
observer = Observer()
observer.schedule(event_handler, watch_dir, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
