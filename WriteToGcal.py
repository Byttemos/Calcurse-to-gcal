from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate():
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

def add_event(eventdetails, service):
    event = {
        'summary': eventdetails,
        'start': {
            'dateTime': (datetime.utcnow() + timedelta(days=1)).isoformat(),
            'timeZone': 'Europe/Copenhagen',
        },
        'end': {
            'dateTime': (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
            'timeZone': 'Europe/Copenhagen',
        },
    }
    created_event = service.events().insert(calendarId='hriskaer@gmail.com', body = event).execute()
    print(f"Created event: {created_event['id']}")


if __name__ == '__main__':
    main()




# added entries: ['11/07/2024 @ 12:00 -> 11/07/2024 @ 13:00|test appointment with timeslot', '11/07/2024 [1] test appointment without timeslot']
# deleted entries: []
