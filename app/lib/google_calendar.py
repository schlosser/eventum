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
    """A client to interact with the Google Calendar API.  Once initialized, it
    can be used to create, update, delete, and move events.

    :ivar service: The Google Calendar service to make requests with.
    :ivar private_calendar_id: str - ID of the private calendar.
    :ivar public_calendar_id: str - ID of the public calendar.
    """

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

        :param event: The event in question.
        :type event: :class:`Event`

        :returns: The ID of ``event``'s calendar.
        :rtype: str
        """
        if event.published:
            return self.public_calendar_id
        return self.private_calendar_id

    def _get_service(self):
        """Generate the Google Calendar service, using the credentials
        generated through the command::

            python manage.py --authorize

        The service object is used to make API requests to Google Calendar, but
        will raise IOError if the credentials file is not generated

        :raises: IOError, NotImplementedError

        :returns: The Google Calendar service.
        """
        storage = Storage(app.config['INSTALLED_APP_CREDENTIALS_PATH'])
        credentials = storage.get()

        if credentials is None:
            raise IOError

        if credentials.invalid == True:
            raise NotImplementedError

        http = httplib2.Http()
        http = credentials.authorize(http)

        return build('calendar', 'v3', http=http)

    def create_event(self, event):
        """Creates the event in Google Calendar.

        :param event: The event to create.
        :type event: :class:`Event`

        :raises: :class:`GoogleCalendarAPIBadStatusLine`,
            :class:`GoogleCalendarAPIErrorNotFound`

        :returns: The Google Calendar API response.
        :rtype: dict
        """

        resource = None
        resource = GoogleCalendarResourceBuilder.event_resource(event)

        calendar_id = self._calendar_id_for_event(event)

        app.logger.info('[GOOGLE_CALENDAR]: Create Event')
        request = self.service.events().insert(calendarId=calendar_id,
                                               body=resource)

        # Execute the request
        created_event = self._execute_request(request)

        # Update the Event with the latest info from the response.
        self._update_event_from_response(event, created_event)

        # Return the Google Calendar response dict
        return created_event

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

        :raises: :class:`GoogleCalendarAPIBadStatusLine`,
            :class:`GoogleCalendarAPIErrorNotFound`,
            :class:`GoogleCalendarAPIMissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """

        # Freshen up stale_event
        event = Event.objects().get(id=stale_event.id)

        if not event.gcal_id:
            # TODO: Why does this happen?
            #
            # If we don't have a reference if it's associate Google Calendar
            # ID, then create it fresh.  This raises still because it
            # *shouldn't* ever happen, but it does.
            self.create_event(stale_event)
            raise GoogleCalendarAPIMissingID('Missing gplus_id. Successfully '
                                             'fell back to create.')

        resource = None
        resource = GoogleCalendarResourceBuilder.event_resource(event,
                                                                for_update=True)

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

        app.logger.info('[GOOGLE_CALENDAR]: Update Event')
        request = self.service.events().update(calendarId=calendar_id,
                                               eventId=event_id_for_update,
                                               body=resource)

        # Send the request, falling back to update if it fails.
        try:
            updated_event = self._execute_request(request)
        except GoogleCalendarAPIErrorNotFound as e:
            self.create_event(event)
            app.logger.warning(e.message)
            message = ('Couldn\'t find event to update. '
                       'Successfully fell back to create.')
            raise GoogleCalendarAPIErrorNotFound(message)

        # Update the Event with the latest info from the response.
        self._update_event_from_response(event, updated_event)

        # Return the Google Calendar response dict
        return updated_event

    def publish_event(self, stale_event):
        """Publish an event, moving it to the public calendar.

        The first argument is called ``stale_event`` because it might have
        outdated fields.  The first thing we do is find a fresh event with it's
        id in mongo.

        :param stale_event: The event to publish
        :type event: :class:`Event`

        :raises: :class:`GoogleCalendarAPIBadStatusLine`,
            :class:`GoogleCalendarAPIErrorNotFound`,
            :class:`GoogleCalendarAPIError`,
            :class:`GoogleCalendarAPIMissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """

        # Freshen up stale_event
        event = Event.objects().get(id=stale_event.id)

        if not event.published:
            raise GoogleCalendarAPIError('Event must have published as `True` before publishing')

        return self.move_event(event, from_id=self.private_calendar_id,
                               to_id=self.public_calendar_id)

    def unpublish_event(self, stale_event):
        """Unpublish an event, moving it to the private calendar.

        The first argument is called ``stale_event`` because it might have
        outdated fields.  The first thing we do is find a fresh event with it's
        id in mongo.

        :param stale_event: The event to publish
        :type event: :class:`Event`

        :raises: :class:`GoogleCalendarAPIBadStatusLine`,
            :class:`GoogleCalendarAPIErrorNotFound`,
            :class:`GoogleCalendarAPIError`,
            :class:`GoogleCalendarAPIMissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """

        # Freshen up stale_event
        event = Event.objects().get(id=stale_event.id)

        if event.published:
            raise GoogleCalendarAPIError('Event must have published as `False` before unpublishing')

        return self.move_event(event, from_id=self.public_calendar_id,
                               to_id=self.private_calendar_id)

    def move_event(self, event, from_id, to_id):
        """Move an event between calendars.

        :param event: Event to move between calendars
        :type event: :class:`Event`
        :param str from_id: Calendar Id to move the event from
        :param str to_id: Calendar ID to move the event to

        :raises: :class:`GoogleCalendarAPIMissingID`,
            :class:`GoogleCalendarAPIErrorNotFound`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        if not event.gcal_id:
            raise GoogleCalendarAPIMissingID()

        app.logger.info('[GOOGLE_CALENDAR]: Move Event')
        request =  self.service.events().move(calendarId=from_id,
                                              eventId=event.gcal_id,
                                              destination=to_id)

        # Execute the request
        try:
            return self._execute_request(request)
        except GoogleCalendarAPIErrorNotFound:
            self._execute_request(event)
            raise GoogleCalendarAPIErrorNotFound('Move failed.  Successfully '
                                                 'fell back to create.')

    def delete_event(self, event, as_exception=False):
        """Delete an event or series from Google Calendar, or cancel a single
        event from a series.

        :param event: The event to delete.
        :type event: :class:`Event`
        :param bool as_exception: Whether or not to cancel this event as an
            exception in a series.  Otherwise, series' will be deleted in their
            entirety.

        :raises: :class:`GoogleCalendarAPIBadStatusLine`,
            :class:`GoogleCalendarAPIErrorNotFound`,
            :class:`GoogleCalendarAPIMissingID`

        :returns: The Google Calendar API response.
        :rtype: dict
        """

        if not event.gcal_id:
            raise GoogleCalendarAPIMissingID()

        calendar_id = self._calendar_id_for_event(event)

        # Create the request
        if as_exception:
            app.logger.info('[GOOGLE_CALENDAR]: Delete Event (as exception)')
            resource = GoogleCalendarResourceBuilder.event_resource(event)
            instance = self._instance_resource_for_event_in_series(event)
            instance.update(resource)
            instance['status'] = u'cancelled'

            request = self.service.events().update(calendarId=calendar_id,
                                                   eventId=instance['id'],
                                                   body=instance)
        else:
            app.logger.info('[GOOGLE_CALENDAR]: Delete Event')
            request = self.service.events().delete(calendarId=calendar_id,
                                                   eventId=event.gcal_id)

        # Execute the request, failing silently if the event has already been
        # deleted from Google Calendar.
        try:
            return self._execute_request(request)
        except HttpError as e:
            # TODO: this codepath will never execute.
            #
            # If the resource has already been deleted, fail quietly.
            app.logger.warning(e)
            raise GoogleCalendarAPIEventAlreadyDeleted

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
        event_start_date = \
            GoogleCalendarResourceBuilder.rfc3339(event.start_datetime())

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
            app.logger.error('Request failed. %s' % response)
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
        """Execute the Google Calendar API request passed in.

        :param request:  The Google Calendar API request object to execute.

        :raises: :class:`GoogleCalendarAPIBadStatusLine`,
            :class:`GoogleCalendarAPIErrorNotFound`

        :returns: The Google Calendar API response.
        :rtype: dict
        """
        try:
            return request.execute()
        except httplib.BadStatusLine as e:
            app.logger.warning('[GOOGLE_CALENDAR]: Got BadStatusLine.  Retrying...')
            try:
                return request.execute()
            except httplib.BadStatusLine as e:
                app.logger.error('[GOOGLE_CALENDAR]: Got BadStatusLine again! Raising.')
                raise GoogleCalendarAPIBadStatusLine('Line: %s, Message: %s' %
                                                     (e.line, e.message))
        except HttpError as e:
            raise GoogleCalendarAPIErrorNotFound(uri=e.uri)
