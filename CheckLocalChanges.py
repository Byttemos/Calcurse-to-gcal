import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler 
import os
from pathlib import Path


def get_entry_type(event):
    if event.src_path == str(home) + '/.calcurse/apts':
        return 'apts'
    if event.src_path == str(home) + '/.calcurse/todo':
        return 'todo'

def on_modified(event):
    if event.event_type == 'modified':
        print(get_entry_type(event))
        

if __name__ == '__main__':
    home = Path.home()
    path = sys.argv[1] if len(sys.argv) > 1 else str(home) + '/.calcurse/'
    event_handler = FileSystemEventHandler()
    event_handler.on_modified = on_modified
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
