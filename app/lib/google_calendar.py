import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage

from app.lib.google_calendar_resource_builder import GoogleCalendarResourceBuilder
from app.lib.error import GoogleCalendarAPIError, GoogleCalendarAPIMissingID
from app import app


class GoogleCalendarAPIClient():

    def __init__(self):
        """Initialize the Google Calendar API Client, with a private and public
        calendar to publish to.
        """
        self.service = self._get_service()
        self.private_calendar_id = app.config['PRIVATE_CALENDAR_ID']
        self.public_calendar_id = app.config['PUBLIC_CALENDAR_ID']

    def _calendar_id_for_event(self, event):
        """Returns the ID for the public or private calendar, depending on
        whether or not the event is published.
        """
        return self.public_calendar_id if event.is_published else self.private_calendar_id


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

    def create_event(self, event):
        """"""
        resource = None
        if event.is_recurring:
            resource = GoogleCalendarResourceBuilder.recurring_event_resource(event)
        else:
            resource = GoogleCalendarResourceBuilder.event_resource(event)

        calendar_id = self._calendar_id_for_event(event)
        print '[GOOGLE_CALENDAR]: Create Event'
        created_event = self.service.events().insert(calendarId=calendar_id,
                                                     body=resource).execute()
        gcal_id = created_event.get('id')
        if not gcal_id:
            raise GoogleCalendarAPIError('Request failed. %s' % created_event)

        if event.is_recurring:
            event.parent_series.gcal_id = gcal_id
            for ev in event.parent_series.events:
                ev.gcal_id = gcal_id
                ev.save()
            event.parent_series.save()
        else:
            event.gcal_id = gcal_id
            event.save()

        return created_event

    def update_event(self, event):
        """"""
        if not event.gcal_id:
            raise GoogleCalendarAPIMissingID()

        resource = None
        if event.is_recurring:
            resource = GoogleCalendarResourceBuilder.recurring_event_resource(event)
        else:
            resource = GoogleCalendarResourceBuilder.event_resource(event)

        calendar_id = self._calendar_id_for_event(event)
        print '[GOOGLE_CALENDAR]: Update Event'
        updated_event = self.service.events().update(calendarId=calendar_id,
                                                     eventId=event.gcal_id,
                                                     body=resource)
        return updated_event

    def publish_event(self, event):
        """Publish an event, moving it to the public calendar.

        - event (Event): The event to publish
        """
        if not event.is_published:
            raise GoogleCalendarAPIError('Event must have is_published as `True` before publishing')

        return self.move_event(event, from_id=self.private_calendar_id,
                               to_id=self.public_calendar_id)

    def unpublish_event(self, event):
        """Unpublish an event, moving it to the private calendar.

        - event (Event): The event to unpublish
        """
        if event.is_published:
            raise GoogleCalendarAPIError('Event must have is_published as `False` before unpublishing')

        return self.move_event(event, from_id=self.public_calendar_id,
                               to_id=self.private_calendar_id)

    def move_event(self, event, from_id, to_id):
        """Move an event between calendars.

        - event (Event): Event to move between calendars
        - from_id (string): Calendar Id to move the event from
        - to_id (string): Calendar ID to move the event to
        """
        if not event.gcal_id:
            raise GoogleCalendarAPIMissingID()

        print '[GOOGLE_CALENDAR]: Move Event'
        return self.service.events().move(calendarId=from_id,
                                          eventId=event.gcal_id,
                                          destination=to_id)

    def delete_event(self, event, calendar_id=None):
        if not event.gcal_id:
            raise GoogleCalendarAPIMissingID()
        if not calendar_id:
            calendar_id = self._calendar_id_for_event(event)

        print '[GOOGLE_CALENDAR]: Delete Event'
        return self.service.events().delete(calendarId=calendar_id,
                                            eventId=event.gcal_id).execute()

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

