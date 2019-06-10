from __future__ import print_function
import datetime
import pickle
import os.path
import traceback
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            except Exception as e:
                traceback.print_exc()
                print ("Error: %s. Please go to https://developers.google.com/calendar/quickstart/python \n and click 'Enable the Google Calendar API' and then 'Download Client Configuration' to continue" % e)
                

    return creds



def get_calendar_events(creds, end_date = None , results=5):

    service = build('calendar', 'v3', credentials=creds)


    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    
    if end_date:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            timeMax=end_date,maxResults=results,
                                            singleEvents=True, orderBy='startTime').execute()
    else:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=results,singleEvents=True,
                                            orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        #print('No upcoming events found.')
        return None
        

    else:
        """
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
        """
        return events
