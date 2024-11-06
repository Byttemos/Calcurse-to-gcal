import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler 
import os
from pathlib import Path
import shutil
import difflib
from WriteToGcal import authenticate, add_event



def get_diffs(event):
    '''compare contents of modified calendar file with reference backup file'''
    modified_src = event.src_path
    entry_types = modified_src[-4:]
    if entry_types == 'apts':
        with open(modified_src, 'r') as modified, open(apt_lastupdate_src, 'r') as lastupdate:

            diff = difflib.unified_diff(
                modified.readlines(),
                lastupdate.readlines(),
            )
        deleted_apts = []
        added_apts = []
        for line in diff:
            #Add changes to arrays for added and deleted entries
            if line.startswith('+') and not line.startswith('++'):
                deleted_apts.append(line[1:].strip())
            if line.startswith('-') and not line.startswith('--'):
                added_apts.append(line[1:].strip())
        # print(f'added appointments: {added_apts}')
        # print(f'deleted appointments: {deleted_apts}')
        #update reference file for next change
        shutil.copyfile(str(home) + '/.calcurse/apts', str(home) + '/.calcurse/apt_lastupdate')
        apt_changes = [added_apts, deleted_apts]
        return format_entries(apt_changes, entry_types)
    if entry_types == 'todo':
        with open(modified_src, 'r') as modified, open(todo_lastupdate_src, 'r') as lastupdate:

            diff = difflib.unified_diff(
                modified.readlines(),
                lastupdate.readlines(),
            )
        deleted_todos = []
        added_todos = []
        for line in diff:
            #Add changes to arrays for added and deleted entries
            if line.startswith('+') and not line.startswith('++'):
                deleted_todos.append(line[1:].strip())
            if line.startswith('-') and not line.startswith('--'):
                added_todos.append(line[1:].strip())
        # print(f'added todos: {added_todos}')
        # print(f'deleted todos: {deleted_todos}')
        #update reference file for next change
        shutil.copyfile(str(home) + '/.calcurse/todo', str(home) + '/.calcurse/todo_lastupdate')
        todo_changes = [added_todos, deleted_todos] 
        return format_entries(todo_changes, entry_types)



def format_entries(entries, entry_types):
    '''Recieve 2d array of added and deleted entries and types, and return google-api compliant dictionaries'''
    def has_timeslot(event_string):
        timeslot_pattern = r'\b\d{2}/\d{2}/\d{4} @ \d{2}:\d{2} -> \d{2}/\d{2}/\d{4} @ \d{2}:\d{2}\b'
        return bool(re.search(timeslot_pattern, event_string))


    def get_event_summary(event_string):
        # Regular expression to match the event with a time range and extract the summary after the `|`
        timeslot_pattern = r'\b\d{2}/\d{2}/\d{4} @ \d{2}:\d{2} -> \d{2}/\d{2}/\d{4} @ \d{2}:\d{2}\b\s*\|\s*(.*)'
        
        # If the event matches the time range pattern (with a '|')
        match = re.search(timeslot_pattern, event_string)
        if match:
            return match.group(1).strip()  # Return the part after the `|`
        
        # Regular expression to match event without a time range
        # This pattern also accounts for the `[n]` identifier after the date
        without_timeslot_pattern = r'\b\d{2}/\d{2}/\d{4} \[\d+\]\s*(.*)'
        
        match = re.search(without_timeslot_pattern, event_string)
        if match:
            return match.group(1).strip()  # Return the remaining part (summary)
        
        return ""  # Return an empty string if no valid summary is found


    print(f'type: {entry_types}')
    print(f'added entries: {entries[0]}')
    print(f'deleted entries: {entries[1]}')
    
    if entry_types == 'apts':
        for entry in entries[0]:
            if has_timeslot(entry)
                event_details = {'summary': get_event_summary(entry), 
                                 'start': {'datetime': }
                                 }
    


            
def on_modified(event):
    '''Filter event types that arent modifications from the eventhandler trigger'''
    #When time comes for reading cloud stored entries, this function will propably also handle runaway loops
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
