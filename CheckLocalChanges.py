import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler 
import os
from pathlib import Path
import shutil
import difflib



def get_diffs(event):
    '''compare contents of modified calendar file with reference backup file'''
    modified_src = event.src_path
    if modified_src[-4:] == 'apts':
        with open(modified_src, 'r') as modified, open(apt_lastupdate_src, 'r') as lastupdate:

            diff = difflib.unified_diff(
                modified.readlines(),
                lastupdate.readlines(),
            )
        for line in diff:
            print(line)
            
    if modified_src[-4:] == 'todo':
        #print('\n'.join(diff))
        print('todo')
    
def on_modified(event):
    '''Filter event types that arent modifications from the eventhandler trigger'''
    if event.event_type == 'modified':
        get_diffs(event)

if __name__ == '__main__':
    home = Path.home()
    if os.path.exists(str(home) + '/.calcurse/apt_lastupdate'):
        apt_lastupdate_src = str(home) + '/.calcurse/apt_lastupdate' 
    else:
        apt_lastupdate_src = shutil.copyfile(str(home) + '/.calcurse/apts', str(home) + '/.calcurse/apt_lastupdate')

    if os.path.exists(str(home) + '/.calcurse/todo_lastupdate'):
        todo_lastupdate_src = str(home) + '/.calcurse/todo_lastupdate' 
    else:
        todo_lastupdate_src = shutil.copyfile(str(home) + '/.calcurse/todo', str(home) + '/.calcurse/todo_lastupdate')


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
