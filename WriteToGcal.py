from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle



def authenticate():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials = creds)

    return service

def add_event(new_entries):
    service = authenticate()

    for entry in new_entries:
        created_event = service.events().insert(calendarId='hriskaer@gmail.com', body = entry).execute()
        print(f"Created event: {created_event['id']}")

# EXAMPLE DATA
# added entries: ['11/07/2024 @ 12:00 -> 11/07/2024 @ 13:00|test appointment with timeslot', 
# '11/07/2024 [1] test appointment without timeslot']
# deleted entries: []

# EXAMPLE DATETIME ISO FORMAT
#        '2024-11-09T17:09:12.079482'
