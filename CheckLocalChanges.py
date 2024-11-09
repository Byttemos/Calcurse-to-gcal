import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler 
import os
from pathlib import Path
import shutil
import difflib
from WriteToGcal import add_event
from datetime import datetime



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

    def has_datetimeslot(event_string):
        '''Receive single event string, return boolean true if it contains a timeslot and false otherwise'''
        if '->' in event_string:
            return True
        if '[1]' in event_string:
            return False


    def get_event_summary(event_string):
        '''Receive single event string, return string containing event summary'''
        if has_datetimeslot(event_string):
            summary = event_string[event_string.find('|')+1:]
            return summary
        if not has_datetimeslot(event_string):
            summary = event_string[event_string.find(']')+1:]
            return summary

    def get_event_datetime(event_string):
        '''Receive single event string, return tuple of ISO-compliant datetime values for start and end time'''

        def get_iso_datetime(date_string, time_string = None):
            '''Receive datetime in a string, convert it to a datetime object and finally convert and return this object in ISO standard format'''
            if time_string:
                datetime_string = date_string + '/' + time_string
                iso_datetime = datetime.strptime(datetime_string, '%m/%d/%Y/%H:%M').isoformat()
                return iso_datetime
            else:
                iso_datetime = datetime.strptime(date_string, '%m/%d/%Y').date().isoformat()
                return iso_datetime

        if has_datetimeslot(event_string):
            dateslot = (event_string[:10], event_string[event_string.find('>')+2:event_string.find('>')+2+10])
            timeslot = (event_string[13:19].strip(), event_string[event_string.find('|')-5:event_string.find('|')])
            iso_formatted_time = (get_iso_datetime(dateslot[0], timeslot[0]), get_iso_datetime(dateslot[1], timeslot[1]))
        if not has_datetimeslot(event_string):
            dateslot = (event_string[:10], event_string[:10])
            iso_formatted_time = (get_iso_datetime(dateslot[0]), get_iso_datetime(dateslot[1]))
        # iso_formatted_time = (get_iso_datetime(dateslot[0], timeslot[0]), get_iso_datetime(dateslot[1], timeslot[1]))
        print(type(iso_formatted_time[0]), type(iso_formatted_time[1]))
        return iso_formatted_time




    print(f'type: {entry_types}')
    print(f'added entries: {entries[0]}')
    print(f'deleted entries: {entries[1]}')
    all_entries = []
    if entry_types == 'apts':
        for entry in entries[0]:
            if has_datetimeslot(entry):
                event_details = {'summary': get_event_summary(entry), 
                                 'start': {
                                    'dateTime': get_event_datetime(entry)[0],
                                    'timeZone': 'Europe/Copenhagen',
                                     },
                                 'end': {
                                    'dateTime': get_event_datetime(entry)[1],
                                    'timeZone': 'Europe/Copenhagen',
                                     },
                                 }
                all_entries.append(event_details)
            if not has_datetimeslot(entry):
                event_details = {'summary': get_event_summary(entry), 
                                  'start': {
                                 'date': get_event_datetime(entry)[0][:10],
                                     'timeZone': 'Europe/Copenhagen',
                                     },
                                    'end': {
                                    'date': get_event_datetime(entry)[1],
                                      'timeZone': 'Europe/Copenhagen',
                                     },
                                 }
                all_entries.append(event_details)
    print(f'entries sent to gcal: {all_entries}')
    add_event(all_entries)

            
def on_modified(event):
    '''Filter event types that arent modifications from the eventhandler trigger, and send formatted new entries to WriteToGcal'''
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
