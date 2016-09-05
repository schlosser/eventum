import httplib2
import httplib
from sys import exit, stderr

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.file import Storage
from flask import current_app

from eventum.models import Event
from eventum.lib.google_calendar_resource_builder import (
    GoogleCalendarResourceBuilder)
from eventum.lib.decorators import skip_and_return_if_auth_disabled
from eventum.lib.error import EventumError

NO_CREDENTIALS = (
    'Failed to find the Google Calendar credentials file at '
    '`{}`, please create it by running:\n\n'
    '    $ python manage.py --authorize\n'
    'The environment variable EVENTUM_GOOGLE_AUTH_ENABLED is currently set to '
    '`{}`.  If set to FALSE, Google Calendar calls will fail silently.')


class GoogleCalendarAPIClient():
    """A client to interact with the Google Calendar API.  Once initialized, it
    can be used to create, update, delete, and move events.

    :ivar service: The Google Calendar service to make requests with.
    :ivar private_calendar_id: str - ID of the private calendar.
    :ivar public_calendar_id: str - ID of the public calendar.
    """

    def __init__(self, app):
        """Initialize the Google Calendar API Client
        """
        self.app = app

        try:
            self.service = self._get_service()
        except IOError:

            # Find the valueof the EVENTUM_GOOGLE_AUTH_ENABLED environment var
            if self.app.config['EVENTUM_GOOGLE_AUTH_ENABLED']:
                gae_environ = 'TRUE'
            else:
                gae_environ = 'FALSE'

            # Print error message
            print >> stderr, NO_CREDENTIALS.format(
                self.app.config['EVENTUM_INSTALLED_APP_CREDENTIALS_PATH'],
                gae_environ)

            # Quit
            exit(1)

    def before_request(self):
        """Refreshes the Google Calendar Service.  It is better practice to
        refresh the service before every request, as opposed to just at the
        beginning of running the app.
        """
        self.service = self._get_service()
        self.private_calendar_id = (
            self.app.config['EVENTUM_PRIVATE_CALENDAR_ID'])
        self.public_calendar_id = (
            self.app.config['EVENTUM_PUBLIC_CALENDAR_ID'])

    def _calendar_id_for_event(self, event):
        """Returns the ID for the public or private calendar, depending on
        whether or not the event is published.

        :param event: The event in question.
        :type event: :class:`Event`

        :returns: The ID of ``event``'s calendar.
        :rtype: str
        """
        if event.published:
            return self.public_calendar_id
        return self.private_calendar_id

    @skip_and_return_if_auth_disabled
    def _get_service(self):
        """Create and return the Google Calendar service object, using the
        credentials file generated through the command::

            python manage.py --authorize

        The service object is used to make API requests to Google Calendar, but
        will raise IOError if the credentials file is not generated

        :raises: IOError, NotImplementedError

        :returns: The Google Calendar service.
        """
        storage = Storage(
            self.app.config['EVENTUM_INSTALLED_APP_CREDENTIALS_PATH'])
        credentials = storage.get()

        if credentials is None:
            raise IOError

        if credentials.invalid is True:
            raise NotImplementedError

        http = httplib2.Http()
        http = credentials.authorize(http)

        return build('calendar', 'v3', http=http)

    @skip_and_return_if_auth_disabled
    def create_event(self, event):
        """Creates the event in Google Calendar.

        :param event: The event to create.
        :type event: :class:`Event`

        :raises: :class:`EventumError.GCalAPI.BadStatusLine`,
            :class:`EventumError.GCalAPI.NotFound`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        self.before_request()

        resource = None
        resource = GoogleCalendarResourceBuilder.event_resource(event)

        calendar_id = self._calendar_id_for_event(event)

        current_app.logger.info('[GOOGLE_CALENDAR]: Create Event')
        request = self.service.events().insert(calendarId=calendar_id,
                                               body=resource)

        # Execute the request
        created_event = self._execute_request(request)

        # Update the Event with the latest info from the response.
        self._update_event_from_response(event, created_event)

        # Return the Google Calendar response dict
        return created_event

    @skip_and_return_if_auth_disabled
    def update_event(self, stale_event, as_exception=False):
        """Updates the event in Google Calendar.

        The first argument is called ``stale_event`` because it might have
        outdated fields.  The first thing we do is find a fresh event with it's
        id in mongo.

        This method will fall back to creating a new event if we don't have
        reference to a ``gcal_id`` for the event, or if the update otherwise
        fails.

        :param stale_event: The event to update.
        :type stale_event: :class:`Event`
        :param bool as_exception: Whether or not this update should happen as
            an exception in a series.  Otherwise, series' will be updated in
            their entirety.

        :raises: :class:`EventumError.GCalAPI.BadStatusLine`,
            :class:`EventumError.GCalAPI.NotFound`,
            :class:`EventumError.GCalAPI.MissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        self.before_request()

        # Freshen up stale_event
        event = Event.objects().get(id=stale_event.id)

        if not event.gcal_id:
            # If we don't have a reference if it's associate Google Calendar
            # ID, then create it fresh.  This raises still because it
            # *shouldn't* ever happen, but it does.
            self.create_event(stale_event)
            raise EventumError.GCalAPI.MissingID.UpdateFellBackToCreate()

        resource = None
        resource = GoogleCalendarResourceBuilder.event_resource(
            event, for_update=True)

        calendar_id = self._calendar_id_for_event(event)

        # If this update should be an exception to a series of events, then
        # we only want to update the instance id.  Otherwise, using the
        # ``event.gcal_id`` will update the entire series.
        event_id_for_update = event.gcal_id
        if as_exception:
            instance = self._instance_resource_for_event_in_series(event)
            instance.update(resource)
            resource = instance
            event_id_for_update = instance['id']

        current_app.logger.info('[GOOGLE_CALENDAR]: Update Event')
        request = self.service.events().update(calendarId=calendar_id,
                                               eventId=event_id_for_update,
                                               body=resource)

        # Send the request, falling back to update if it fails.
        try:
            updated_event = self._execute_request(request)
        except EventumError.GCalAPI.NotFound as e:
            self.create_event(event)
            raise EventumError.GCalAPI.NotFound.UpdateFellBackToCreate(e=e)

        # Update the Event with the latest info from the response.
        self._update_event_from_response(event, updated_event)

        # Return the Google Calendar response dict
        return updated_event

    @skip_and_return_if_auth_disabled
    def publish_event(self, stale_event):
        """Publish an event, moving it to the public calendar.

        The first argument is called ``stale_event`` because it might have
        outdated fields.  The first thing we do is find a fresh event with it's
        id in mongo.

        :param stale_event: The event to publish
        :type event: :class:`Event`

        :raises: :class:`EventumError.GCalAPI.BadStatusLine`,
            :class:`EventumError.GCalAPI.NotFound`,
            :class:`EventumError.GCalAPI.Error`,
            :class:`EventumError.GCalAPI.MissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        self.before_request()

        # Freshen up stale_event
        event = Event.objects().get(id=stale_event.id)

        if not event.published:
            raise EventumError.GCalAPI.PublishFailed.PublishedFalse()

        return self.move_event(event, from_id=self.private_calendar_id,
                               to_id=self.public_calendar_id)

    @skip_and_return_if_auth_disabled
    def unpublish_event(self, stale_event):
        """Unpublish an event, moving it to the private calendar.

        The first argument is called ``stale_event`` because it might have
        outdated fields.  The first thing we do is find a fresh event with it's
        id in mongo.

        :param stale_event: The event to publish
        :type event: :class:`Event`

        :raises: :class:`EventumError.GCalAPI.BadStatusLine`,
            :class:`EventumError.GCalAPI.NotFound`,
            :class:`EventumError.GCalAPI.Error`,
            :class:`EventumError.GCalAPI.MissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        self.before_request()

        # Freshen up stale_event
        event = Event.objects().get(id=stale_event.id)

        if event.published:
            raise EventumError.GCalAPI.PublishFailed.PublishedTrue()

        return self.move_event(event, from_id=self.public_calendar_id,
                               to_id=self.private_calendar_id)

    @skip_and_return_if_auth_disabled
    def move_event(self, event, from_id, to_id):
        """Move an event between calendars.

        :param event: Event to move between calendars
        :type event: :class:`Event`
        :param str from_id: Calendar Id to move the event from
        :param str to_id: Calendar ID to move the event to

        :raises: :class:`EventumError.GCalAPI.MissingID`,
            :class:`EventumError.GCalAPI.NotFound`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        if not event.gcal_id:
            raise EventumError.GCalAPI.MissingID()

        current_app.logger.info('[GOOGLE_CALENDAR]: Move Event')
        request = self.service.events().move(calendarId=from_id,
                                             eventId=event.gcal_id,
                                             destination=to_id)

        # Execute the request
        try:
            return self._execute_request(request)
        except EventumError.GCalAPI.NotFound as e:
            self.create_event(event)
            raise EventumError.GCalAPI.NotFound.MoveFellBackToCreate(uri=e.uri)

    @skip_and_return_if_auth_disabled
    def delete_event(self, event, as_exception=False):
        """Delete an event or series from Google Calendar, or cancel a single
        event from a series.

        :param event: The event to delete.
        :type event: :class:`Event`
        :param bool as_exception: Whether or not to cancel this event as an
            exception in a series.  Otherwise, series' will be deleted in their
            entirety.

        :raises: :class:`EventumError.GCalAPI.BadStatusLine`,
            :class:`EventumError.GCalAPI.NotFound`,
            :class:`EventumError.GCalAPI.MissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        self.before_request()

        if not event.gcal_id:
            raise EventumError.GCalAPI.MissingID()

        calendar_id = self._calendar_id_for_event(event)

        # Create the request
        if as_exception:
            current_app.logger.info(
                '[GOOGLE_CALENDAR]: Delete Event (as exception)')
            resource = GoogleCalendarResourceBuilder.event_resource(event)
            instance = self._instance_resource_for_event_in_series(event)
            instance.update(resource)
            instance['status'] = u'cancelled'

            request = self.service.events().update(calendarId=calendar_id,
                                                   eventId=instance['id'],
                                                   body=instance)
        else:
            current_app.logger.info('[GOOGLE_CALENDAR]: Delete Event')
            request = self.service.events().delete(calendarId=calendar_id,
                                                   eventId=event.gcal_id)

        # Execute the request, failing silently if the event has already been
        # deleted from Google Calendar.
        try:
            return self._execute_request(request)
        except EventumError.GCalAPI.NotFound as e:
            # If the resource has already been deleted, fail quietly.
            raise EventumError.GCalAPI.EventAlreadyDeleted(e=e)

    def _instance_resource_for_event_in_series(self, event):
        """Searches through the instances of ``event``'s parent series,
        returning the Google Calendar instance resource for with ``start_time``
        that matches ``event``'s.

        :param event: The event to find the instance resource for.
        :type event: :class:`Event`

        :returns: The instance resource that represents ``event``.
        :rtype: dict
        """
        calendar_id = self._calendar_id_for_event(event)
        event_start_date = (GoogleCalendarResourceBuilder
                            .rfc3339(event.start_datetime))
        page_token = None
        while True:
            # Find more instances
            request = self.service.events().instances(calendarId=calendar_id,
                                                      eventId=event.gcal_id,
                                                      pageToken=page_token)
            instances = self._execute_request(request)

            # Look for instances with matching start date
            for instance in instances['items']:
                if instance['start']['dateTime'] == event_start_date:
                    return instance

            # Get the next page of events
            page_token = instances.get('nextPageToken')

            # Quit if there are no more pages
            if not page_token:
                break

        return None

    def _update_event_from_response(self, event, response):
        """Updates ``event`` using new fields from ``response``.

        :param event: The event to update.
        :type event: :class:`Event`
        :param dict response: The Google Calendar API response to search for
            updates in.

        :raises: GoogleCalendarAPIError
        """
        gcal_id = response.get('id')
        gcal_sequence = response.get('sequence')
        if gcal_id is None or gcal_sequence is None:
            raise EventumError.GCalAPI(response=response)

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
        """Execute the Google Calendar API request passed in.

        :param request:  The Google Calendar API request object to execute.

        :raises: :class:`EventumError.GCalAPI.BadStatusLine`,
            :class:`EventumError.GCalAPI.NotFound`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        try:
            return request.execute()
        except httplib.BadStatusLine as e:
            # Google Calendar returned a empty status line.
            raise EventumError.GCalAPI.BadStatusLine(message=e.message,
                                                     line=e.line)
        except HttpError as e:
            raise EventumError.GCalAPI.NotFound(uri=e.uri)
