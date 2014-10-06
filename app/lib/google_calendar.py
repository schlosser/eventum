import httplib2
import httplib
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.file import Storage

from app.lib.google_calendar_resource_builder import GoogleCalendarResourceBuilder
from app.lib.error import (GoogleCalendarAPIError,
                           GoogleCalendarAPIMissingID,
                           GoogleCalendarAPIBadStatusLine,
                           GoogleCalendarAPIEventAlreadyDeleted,
                           GoogleCalendarAPIErrorNotFound)
from app import app
from app.models import Event


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
        return self.public_calendar_id if event.published else self.private_calendar_id


    def _get_service(self):
        """Generate the Google Calendar service, using the credentials
        generated through the command:

        $ python manage.py --authorize

        The service object is used to make API requests to Google Calendar, but
        will raise IOError if the credentials file is not generated
        """
        storage = Storage(app.config['INSTALLED_APP_SECRET_PATH'])
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
        resource = GoogleCalendarResourceBuilder.event_resource(event)

        calendar_id = self._calendar_id_for_event(event)

        print '[GOOGLE_CALENDAR]: Create Event'
        request = self.service.events().insert(calendarId=calendar_id,
                                               body=resource)
        created_event = self._execute_request(request)

        self._update_event_from_response(event, created_event)

        return created_event

    def update_event(self, stale_event, as_exception=False):
        """"""
        event = Event.objects().get(id=stale_event.id)

        if not event.gcal_id:
            self.create_event(stale_event)
            raise GoogleCalendarAPIMissingID('Missing gplus_id. Successfully fell back to create.')

        resource = None
        resource = GoogleCalendarResourceBuilder.event_resource(event,
                                                                for_update=True)

        calendar_id = self._calendar_id_for_event(event)
        event_id_for_update = event.gcal_id
        if as_exception:
            instance = self._instance_resource_for_event_in_series(event)
            instance.update(resource)
            resource = instance
            event_id_for_update = instance['id']

        print '[GOOGLE_CALENDAR]: Update Event'
        request = self.service.events().update(calendarId=calendar_id,
                                               eventId=event_id_for_update,
                                               body=resource)
        try:
            updated_event = self._execute_request(request)
        except GoogleCalendarAPIErrorNotFound as e:
            self.create_event(event)
            print e.message
            raise GoogleCalendarAPIErrorNotFound('Couldn\'t find event to update. '
                                                 'Successfully fell back to create.')

        self._update_event_from_response(event, updated_event)

        return updated_event

    def publish_event(self, stale_event):
        """Publish an event, moving it to the public calendar.

        - event (Event): The event to publish
        """
        event = Event.objects().get(id=stale_event.id)

        if not event.published:
            raise GoogleCalendarAPIError('Event must have published as `True` before publishing')

        return self.move_event(event, from_id=self.private_calendar_id,
                               to_id=self.public_calendar_id)

    def unpublish_event(self, stale_event):
        """Unpublish an event, moving it to the private calendar.

        - event (Event): The event to unpublish
        """
        event = Event.objects().get(id=stale_event.id)

        if event.published:
            raise GoogleCalendarAPIError('Event must have published as `False` before unpublishing')

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
        request =  self.service.events().move(calendarId=from_id,
                                              eventId=event.gcal_id,
                                              destination=to_id)
        try:
            return self._execute_request(request)
        except GoogleCalendarAPIErrorNotFound:
            self._execute_request(event)
            raise GoogleCalendarAPIErrorNotFound('Move failed.  Successfully fell back to create.')

    def delete_event(self, event, as_exception=False):
        if not event.gcal_id:
            raise GoogleCalendarAPIMissingID()

        calendar_id = self._calendar_id_for_event(event)

        if as_exception:
            print '[GOOGLE_CALENDAR]: Delete Event (as exception)'
            resource = GoogleCalendarResourceBuilder.event_resource(event)
            instance = self._instance_resource_for_event_in_series(event)
            instance.update(resource)
            instance['status'] = u'cancelled'

            request = self.service.events().update(calendarId=calendar_id,
                                                   eventId=instance['id'],
                                                   body=instance)
        else:
            print '[GOOGLE_CALENDAR]: Delete Event'
            request = self.service.events().delete(calendarId=calendar_id,
                                                   eventId=event.gcal_id)
        try:
            return self._execute_request(request)
        except HttpError as e:
            # If the resource has already been deleted, fail quietly.
            print e
            raise GoogleCalendarAPIEventAlreadyDeleted

    def get_calendar_list_resources(self):
        """"""
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

    def _instance_resource_for_event_in_series(self, event):
        """"""
        calendar_id = self._calendar_id_for_event(event)
        event_start_date = GoogleCalendarResourceBuilder.rfc3339(event.start_datetime())

        page_token = None
        while True:
          instances = self.service.events().instances(calendarId=calendar_id,
                                                      eventId=event.gcal_id,
                                                      pageToken=page_token).execute()
          for instance in instances['items']:
            if instance['start']['dateTime'] == event_start_date:
                return instance
          page_token = instances.get('nextPageToken')
          if not page_token:
            break

        return None

    def _update_event_from_response(self, event, response):
        """"""
        gcal_id = response.get('id')
        gcal_sequence = response.get('sequence')
        if gcal_id is None or gcal_sequence is None:
            print 'Request failed. %s' % response
            raise GoogleCalendarAPIError('Request Failed.')

        if event.is_recurring:
            event.parent_series.gcal_id = gcal_id
            for ev in event.parent_series.events:
                ev.gcal_id = gcal_id
                ev.gcal_sequence = gcal_sequence
                ev.save()
            event.parent_series.save()
        else:
            event.gcal_id = gcal_id
            event.gcal_sequence = gcal_sequence
            event.save()

    def _execute_request(self, request):
        """"""
        try:
            return request.execute()
        except httplib.BadStatusLine as e:
            print e.line, e.message
            print '[GOOGLE_CALENDAR]: Got BadStatusLine.  Retrying...'
            try:
                return request.execute()
            except httplib.BadStatusLine as e:
                print '[GOOGLE_CALENDAR]: Got BadStatusLine again! Raising.'
                raise GoogleCalendarAPIBadStatusLine('Line: %s, Message: %s' %
                                                     (e.line, e.message))
        except HttpError as e:
            raise GoogleCalendarAPIErrorNotFound(uri=e.uri)
