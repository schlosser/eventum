import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage

from app.lib.google_calendar_resource_builder import GoogleCalendarResourceBuilder
from app import app

class GoogleCalendarAPIClient():

    def __init__(self):
        """Initialize the Google Calendar API Client, with a private and public
        calendar to publish to.
        """
        self.service = self._get_service()
        self.private_calendar_id = app.config['PRIVATE_CALENDAR_ID']
        self.public_calendar_id = app.config['PUBLIC_CALENDAR_ID']


    def _get_service(self):
        """Generate the Google Calendar service, using the credentials
        generated through the command:

        $ python manage.py --authorize

        The service object is used to make API requests to Google Calendar, but
        will raise IOError if the credentials file is not generated
        """
        storage = Storage(app.config['CREDENTIALS_PATH'])
        credentials = storage.get()

        if credentials is None:
            raise IOError

        if credentials.invalid == True:
            raise NotImplementedError

        http = httplib2.Http()
        http = credentials.authorize(http)

        return build('calendar', 'v3', http=http)

    def publish_event(self, event):
        event_resource = GoogleCalendarResourceBuilder.build_longform_from_event(event)
        created_event = self.service.events().insert(calendarId='primary', body=event_resource).execute()
        print created_event
        print created_event['id']

    def get_calendar_list_resources(self):
        calendar_list_resources = []
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                calendar_list_resources.append(calendar_list_entry)
                page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        return calendar_list_resources

