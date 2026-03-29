import os
import sys
import datetime
import pickle

try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.exceptions import RefreshError
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    sys.stderr.write("Warning: Google Calendar support not available. Install with: pip install 'kueche[google-calendar]'\n")

from .userpanel import UserPanel


class Kalender(UserPanel):

    def __init__(self, google_secret, calendar_id, lcars_app):
        UserPanel.__init__(self, 'KALENDER', lcars_app.menue.pages)
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.CLIENT_SECRET_FILE = google_secret
        self.APPLICATION_NAME = 'Kueche Calendar'
        self.calendar_id = str(calendar_id)
        self.service = None

        if GOOGLE_CALENDAR_AVAILABLE:
            self._init_service()

    def get_credentials(self):
        """Get OAuth2 credentials using the new google-auth library"""
        if not GOOGLE_CALENDAR_AVAILABLE:
            return None

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'kueche-calendar.pickle')

        creds = None

        # Load existing credentials from pickle file
        if os.path.exists(credential_path):
            with open(credential_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, run the OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired credentials
                try:
                    creds.refresh(Request())
                except RefreshError:
                    # Token refresh failed, need to re-authenticate
                    creds = None

            if not creds:
                # Run the OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(credential_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def _init_service(self):
        """Initialize Google Calendar service"""
        if not GOOGLE_CALENDAR_AVAILABLE:
            return

        try:
            creds = self.get_credentials()
            if creds:
                self.service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            sys.stderr.write("Error initializing Google Calendar service: {}\n".format(e))

    def get_events(self, number=5):
        if not GOOGLE_CALENDAR_AVAILABLE:
            return []

        # Reinitialize service if not available
        if not self.service:
            self._init_service()

        if not self.service:
            return []

        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            print('Getting the upcoming {} events: {}'.format(number, self.calendar_id))

            # Get events from specified calendar
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=number,
                singleEvents=True,
                orderBy='startTime').execute()

            # Get events from primary calendar
            events_resultP = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=number,
                singleEvents=True,
                orderBy='startTime').execute()

            items = events_result.get('items', [])
            items = items + events_resultP.get('items', [])

            # Normalize datetime format
            for item in items:
                start = item['start']
                if 'dateTime' not in start:
                    start['dateTime'] = start['date'] + 'T00:00:00Z'

            items = sorted(items, key=lambda event: event['start']['dateTime'])
            return items

        except Exception as e:
            sys.stderr.write("Error fetching calendar events: {}\n".format(e))
            return []
