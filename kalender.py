from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import argparse


#from observerable import Observable
from userpanel import UserPanel


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


class Kalender(UserPanel):

    def __init__(self, google_secret, calendar_id, lcars_app):
        UserPanel.__init__(self, 'KALENDER', lcars_app.menue.pages)
        self.SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
        self.CLIENT_SECRET_FILE = google_secret
        self.APPLICATION_NAME = 'Google Calendar API Python Quickstart'
        self.calendar_id = str(calendar_id)

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            credentials = tools.run_flow(flow, store, flags)
            # print('Storing credentials to ' + credential_path)
        return credentials

    def get_events(self, number=5):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events :' + self.calendar_id)

        events_result = service.events().list(
            # calendarId='family18212381221434694046@group.calendar.google.com', timeMin=now, maxResults=number, singleEvents=True, orderBy='startTime').execute()
            calendarId=self.calendar_id, timeMin=now, maxResults=number,
            singleEvents=True, orderBy='startTime').execute()
        events_resultP = service.events().list(
            calendarId='primary', timeMin=now, maxResults=number, singleEvents=True, orderBy='startTime').execute()

        items = events_result.get('items', [])
        items = items + events_resultP.get('items', [])
        # date = event['start'][u'dateTime']
        # u'dateTime': u'2018-02-02T09:00:00Z'
        # u'date'    : u'2018-01-22'
        for item in items:
            start = item['start']
            if u'dateTime' not in start:
                start[u'dateTime'] = start[u'date'] + u'T00:00:00Z'
        items = sorted(items, key=lambda event: event['start'][u'dateTime'])

        # for item in items:
        #    print (item['start'][u'dateTime']+ " "+ item[u'summary'])

        return items

        # if not events:
        #    print('No upcoming events found.')
        # for event in events:
        #    start = event['start'].get('dateTime', event['start'].get('date'))
        #    print(start, event['summary'])
