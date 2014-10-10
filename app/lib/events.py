"""
.. module:: events
    :synopsis: This module contains classes that aid in the translation from
        Mongoengine events to Google Calendar events and WTForms.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>

This file passes around data in several forms, which can be confusing.
If we are not dealing with an instance of :class:`CreateEventForm` or a
subclass, a Mongoengine object like :class:`Event` or
:class:`EventSeries`, then we are probably dealing with a dictionary
representing an intermediate form.  These forms include:

``event_data``::

    {
        'title': 'My Event',
        'slug': 'my-event',
        'location': '742 Evergreen Terrace',
        'start_time': datetime.time(13, 0, 0, 0),
        'end_time': datetime.time(14, 30, 0, 0),
        'published': True,
        'short_description_markdown': 'Come to my event',
        'long_description_markdown': 'I swear, it\'ll be *great*!`,
        'is_recurring': False,
        'facebook_url': 'http://facebook.com/events/123456789012345',
        'image': 'simpsons.png'
    }

    ``date_data``::

    {
        'start_date': datetime.date(2014, 10, 4),
        'end_date': datetime.date(2014, 10, 4),
    }

    ``series_data``::


    {
        'frequency': 'weekly',
        'every': 1,
        'slug': 'my-event',
        'ends_on': True,
        'ends_after': False,
        'num_occurrences': 5,
        'recurrence_summary': 'Every 1 week for 5 occurrences.'
    }

    # OR:

    {
        'frequency': 'weekly',
        'every': 1,
        'slug': 'my-event,
        'ends_on': False,
        'ends_after': True,
        'recurrence_end_date': datetime.date(2014, 10, 4),
        'recurrence_summary': 'Every 1 week, ending on October 4th.'
    }

    ``form_data``::

    {
        'title': 'My Event',
        'slug': 'my-event',
        'location': '742 Evergreen Terrace',
        'start_date': datetime.date(2014, 10, 4),
        'start_time': datetime.time(13, 0, 0, 0),
        'end_date': datetime.date(2014, 10, 4),
        'end_time': datetime.time(14, 30, 0, 0),
        'published': True,
        'short_description_markdown': 'Come to my event',
        'long_description_markdown': 'I swear, it\'ll be *great*!`,
        'is_recurring': False,
        'facebook_url': 'http://facebook.com/events/123456789012345',
        'event_image': 'simpsons.png'
    }
"""

from app.models import Event, EventSeries, Image
from app.forms import CreateEventForm
from datetime import timedelta
from app import gcal_client
from app.lib.error import GoogleCalendarAPIError


class EventsHelper(object):
    """A class with helper functions that translate WTForms to Mongoengine
    models and Google Calendar models.

    In general, :class:`EventsHelper` should only be used to call:

    - :func:`create_form`
    - :func:`create_event`
    - :func:`update_event`
    - :func:`delete_event`
    """

    PUBLIC = 'public'
    PRIVATE = 'private'


    ###########################################################################
    # Public API:
    # - create_form
    # - create_event
    # - update_event
    # - delete_event
    ###########################################################################

    @classmethod
    def create_form(klass, event, request):
        """Create an instance of :class:`CreateEventForm` from an event from the
        database and the request object.

        :param event: The event from Mongoengine.
        :type event: :class:`Event`
        :param request: The flask reqeust object, from which we'll make the
            form.  On most requests, this will not contribute to any change in
            how the form is created, but it is a required parameter for
            creating a subclass of :class:`flask.ext.wtforms.Form`.
        :type request: :class:`flask.Request`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: The created form.
        :rtype: :class:`CreateEventForm`
        """

        form_data = DataBuilder.form_data_from_event(event)
        if event.parent_series:
            updates = DataBuilder.form_data_from_series(event.parent_series)
            form_data.update(updates)
        form_data = klass._remove_none_fields(form_data)
        return CreateEventForm(request.form, **form_data)

    @classmethod
    def create_event(klass, form, creator):
        """Creates a Mongoengine and Google Calendar event from form data.

        Calls either :func:`create_series` or :func:`create_single_event`
        depending on whether or not the event should be recurring.

        :param form: The WTForms form.
        :type form: :class:`CreateEventForm` or a subclass.
        :param creator: The user that is currently logged in.
        :type creator: :class:`~app.models.User`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        if form.is_recurring.data:
            # Series
            return klass.create_series(form, creator)
        # Single event
        return klass.create_single_event(form, creator)

    @classmethod
    def update_event(klass, event, form):
        """Updates ``event``, syncing changes to Google Calendar.

        Calls either :func:`update_series`, :func:`update_single_event`, or
        :func:`update_single_event_from_series` depending on whether the
        event is recurring and whether all updates in a series should be
        updated.

        If the event is being made recurring, or a recurrence is being removed,
        :func:`convert_to_series` or :func:`convert_to_single_event` will
        be called instead.

        :param event: The event to update.
        :type event: :class:`Event`
        :param form: The WTForms form from which the updates come.
        :type form: :class:`CreateEventForm` or a subclass.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        # Determine if the event should be moved between calendars
        move_to = None
        if event.published != form.published.data:
            move_to = klass.PUBLIC if form.published.data else klass.PRIVATE

        if event.is_recurring != form.is_recurring.data:
            if event.is_recurring:
                # Series -> single event
                return klass.convert_to_single_event(event,
                                                     form,
                                                     move_to=move_to)
            # Single event -> series
            return klass.convert_to_series(event, form, move_to=move_to)

        elif event.is_recurring:
            if form.update_all.data:
                # Entire series
                return klass.update_series(event, form, move_to=move_to)
            # Single event from series
            return klass.update_single_event_from_series(event, form)
        # Single event
        return klass.update_single_event(event, form, move_to=move_to)

    @classmethod
    def delete_event(klass, event, form):
        """Deletes ``event``, syncing changes to Google Calendar.

        Calls either :func:`delete_series`, :func:`delete_single_event`, or
        :func:`delete_single_event_from_series` depending on whether the
        event is recurring and whether all updates in a series should be
        deleted.

        :param event: The event to delete.
        :type event: :class:`Event`
        :param form: The WTForms form that specifies whether or not all events
            in a series should be deleted, or just a single event.
        :type form: :class:`DeleteEventForm`.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        if event.is_recurring:
            if form.delete_all.data:
                # Series
                return klass.delete_series(event)
            # Single event from series
            return klass.delete_single_event_from_series(event)
        # Single event
        return klass.delete_single_event(event)


    ###########################################################################
    # Worker Methods.
    #
    # These should be called only from their public API method (above).
    ###########################################################################

    @classmethod
    def create_single_event(klass, form, creator):
        """Creates a non-recurring Mongoengine and Google Calendar event from
        form data.

        :param form: The WTForms form.
        :type form: :class:`CreateEventForm` or a subclass.
        :param creator: The user that is currently logged in.
        :type creator: :class:`~app.models.User`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        # Generate the event and date data
        event_and_date_data = DataBuilder.event_and_date_data_from_form(form,
                                                                        creator=creator)
        event_and_date_data = klass._remove_none_fields(event_and_date_data)

        event = Event(**event_and_date_data)
        event.save()

        # Return the Google Calendar response
        return gcal_client.create_event(event)

    @classmethod
    def create_series(klass, form, creator):
        """Creates a recurring Mongoengine and Google Calendar event from
        form data.

        Creates both a :class:`EventSeries` and its associated :class:`Event`s.

        :param form: The WTForms form.
        :type form: :class:`CreateEventForm` or a subclass.
        :param creator: The user that is currently logged in.
        :type creator: :class:`~app.models.User`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        event_data = DataBuilder.event_data_from_form(form, creator=creator)
        date_data = DataBuilder.date_data_from_form(form)

        # Make the parent series
        series = klass._make_series(form)

        # Update event_data with the parent series
        event_data['parent_series'] = series

        # Make the individual Event objects in the series
        while klass._more_events(series, date_data):
            ev = klass._make_event(event_data, date_data)
            series.events.append(ev)
            klass._increment_date_data(series, date_data)

        series.save()

        # Return the Google Calendar response
        return gcal_client.create_event(series.events[0])

    @classmethod
    def update_single_event(klass, event, form, move_to=None):
        """Updates the non-recurring ``event``, syncing changes to Google
        Calendar.

        If ``move_to`` is set to ``"public"`` or ``"private"`` the event
        will also be moved to that calendar.

        :param event: The event to update.
        :type event: :class:`Event`
        :param form: The WTForms form from which the updates come.
        :type form: :class:`CreateEventForm` or a subclass.
        :param str move_to: The calendar to move the event to, if any.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        event_and_date_data = DataBuilder.event_and_date_data_from_form(form)
        event_and_date_data = klass._remove_none_fields(event_and_date_data)
        klass._update_event(event, event_and_date_data)

        # Update the event in Google Calendar and publish it as necessary
        if move_to == klass.PUBLIC:
            response = gcal_client.publish_event(event)
        elif move_to == klass.PRIVATE:
            response = gcal_client.unpublish_event(event)
        response = gcal_client.update_event(event)

        # Return the Google Calendar response
        return response

    @classmethod
    def update_series(klass, event, form, move_to=None):
        """Updates the recurring ``event``, syncing changes to Google Calendar.

        If ``move_to`` is set to ``"public"`` or ``"private"`` the event
        will also be moved to that calendar.

        :param event: The event to update.
        :type event: :class:`Event`
        :param form: The WTForms form from which the updates come.
        :type form: :class:`CreateEventForm` or a subclass.
        :param str move_to: The calendar to move the event to, if any.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        # Build the event, date, and series data, validating the series data.
        event_data = DataBuilder.event_data_from_form(form)
        date_data = DataBuilder.date_data_from_form(form)
        series_data = DataBuilder.series_data_from_form(form)
        klass._validate_series_data(series_data)

        if klass._changes_are_easy(event, series_data, date_data):
            # If changes are easy, then we can make them on the Event objects
            # that already exist.
            for e in event.parent_series.events:
                # the date data isn't changing, so pass in {}
                klass._update_event(e, event_data, {})
            series = event.parent_series
        else:
            # Otherwise, they changes are hard, and we have to create fresh
            # Events.
            shared_gcal_id = event.gcal_id
            shared_gcal_sequence = event.gcal_sequence
            shared_creator = event.creator

            event.parent_series.delete_all()
            series = klass._make_series(None,
                                        gcal_id=shared_gcal_id,
                                        **series_data)

            # Update event_data with the parent series
            event_data['parent_series'] = series
            event_data['gcal_id'] = shared_gcal_id
            event_data['gcal_sequence'] = shared_gcal_sequence
            event_data['creator'] = shared_creator

            # Make the individual Event objects in the series
            while klass._more_events(series, date_data):
                ev = klass._make_event(event_data, date_data)
                series.events.append(ev)
                klass._increment_date_data(series, date_data)

            series.save()

        # Update the event in Google Calendar and publish it as necessary
        if move_to == klass.PUBLIC:
            response = gcal_client.publish_event(series.events[0])
        elif move_to == klass.PRIVATE:
            response = gcal_client.unpublish_event(series.events[0])
        response = gcal_client.update_event(series.events[0])

        # Return Google Calendar response
        return response

    @classmethod
    def update_single_event_from_series(klass, event, form):
        """Updates the ``event`` as an exception to a series, syncing changes
        to Google Calendar.

        The parameter ``move_to`` is not implemented in this method because
        having multiple events in a series on different calendars is not
        possible.

        :param event: The event to update.
        :type event: :class:`Event`
        :param form: The WTForms form from which the updates come.
        :type form: :class:`CreateEventForm` or a subclass.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        event_and_date_data = DataBuilder.event_and_date_data_from_form(form)
        event_and_date_data = klass._remove_none_fields(event_and_date_data)
        klass._update_event(event, event_and_date_data)

        # Return Google Calendar response
        return gcal_client.update_event(event, as_exception=True)

    @classmethod
    def convert_to_series(klass, event, form, move_to=None):
        """Converts ``event`` to be a series and updates other fields, syncing
        changes to Google Calendar.

        If ``move_to`` is set to ``"public"`` or ``"private"`` the event
        will also be moved to that calendar.

        :param event: The event to update.
        :type event: :class:`Event`
        :param form: The WTForms form from which the updates come.
        :type form: :class:`CreateEventForm` or a subclass.
        :param str move_to: The calendar to move the event to, if any.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        event_data = DataBuilder.event_data_from_form(form)
        date_data = DataBuilder.date_data_from_form(form)

        # Make the parent series
        series = klass._make_series(form, gcal_id=event.gcal_id)

        # Update event_data with the parent series
        event_data['parent_series'] = series
        event_data['creator'] = event.creator
        event_data['gcal_id'] = event.gcal_id

        klass._update_event(event, event_data, date_data)
        series.events.append(event)
        klass._increment_date_data(series, date_data)

        # Make the individual Event objects in the series
        while klass._more_events(series, date_data):
            ev = klass._make_event(event_data, date_data)
            series.events.append(ev)
            klass._increment_date_data(series, date_data)

        series.save()

        # Return the Google Calendar response
        return gcal_client.update_event(series.events[0])

    @classmethod
    def convert_to_single_event(klass, event, form, move_to=None):
        """Converts ``event`` from a series to a single event, updating other
        fields and syncing changes to Google Calendar.

        If ``move_to`` is set to ``"public"`` or ``"private"`` the event
        will also be moved to that calendar.

        :param event: The event to update.
        :type event: :class:`Event`
        :param form: The WTForms form from which the updates come.
        :type form: :class:`CreateEventForm` or a subclass.
        :param str move_to: The calendar to move the event to, if any.

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        event_data = DataBuilder.event_data_from_form(form)
        date_data = DataBuilder.date_data_from_form(form)

        event.parent_series.delete_all_except(event)
        klass._update_event(event, date_data, event_data)

        # Delete the series and create a single event
        return gcal_client.update_event(event)


    @classmethod
    def delete_single_event(klass, event):
        """Deletes the non-recurring ``event``, syncing changes to Google
        Calendar.

        :param event: The event to delete.
        :type event: :class:`Event`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        # We have to delete on Google Calendar first, but we should delete the
        # event from MongoEngine even if Google Calendar throws an error.
        try:
            response = gcal_client.delete_event(event)
            event.delete()
        except GoogleCalendarAPIError as e:
            event.delete()
            raise e

        # Return the Google Calendar response
        return response

    @classmethod
    def delete_single_event_from_series(klass, event):
        """Deletes ``event`` from it's parent series, syncing changes to Google
        Calendar.

        :param event: The event to delete.
        :type event: :class:`Event`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        # We have to delete on Google Calendar first, but we should delete the
        # event from MongoEngine even if Google Calendar throws an error.
        try:
            # Cancel the series on Google Calendar
            response = gcal_client.delete_event(event, as_exception=True)
            event.parent_series.delete_one(event)
        except GoogleCalendarAPIError as e:
            event.parent_series.delete_one(event)
            raise e

        # Return the Google Calendar response
        return response

    @classmethod
    def delete_series(klass, event):
        """Deletes the recurring ``event`, syncing changes to Google Calendar.

        :param event: The event to delete.
        :type event: :class:`Event`

        :raises: :class:`GoogleCalendarAPIError` and it's subclasses

        :returns: Response from the Google Calendar API.
        :rtype: dict
        """

        # We have to delete on Google Calendar first, but we should delete the
        # event from MongoEngine even if Google Calendar throws an error.
        try:
            response = gcal_client.delete_event(event)
            event.parent_series.delete_all()
        except GoogleCalendarAPIError as e:
            event.parent_series.delete_all()
            raise e

        # Return the Google Calendar response
        return response


    ###########################################################################
    # Private Helpers
    ###########################################################################

    @classmethod
    def _remove_none_fields(klass, d):
        """removes any fields in ``d`` that are ``None`` and returns ``d``.

        :param dict d: The dictionary to strip ``None`` fields from.

        :returns: ``d`` with all non-``None`` fields.
        :rtype: dict
        """

        return dict((k, v) for k, v in d.iteritems() if v is not None)

    @classmethod
    def _increment_date_data(klass, series, date_data):
        """Increment the start and end date in ``date_data`` for a recurring
        event by the appropriate amount depending on how frequently the event
        occurs.

        If the event is bi-weekly, 14 days will be added to the start and end
        date in ``date_data``

        :param series: The event series which holds how frequently the event
            repeats.
        :type series: :class:`EventSeries`.
        :param dict date_data: The dictionary to increment values in.
        """

        # delta is the timedelta in between events
        delta = timedelta(days=7 * series.every)
        date_data['start_date'] = date_data['start_date'] + delta
        date_data['end_date'] = date_data['end_date'] + delta

    @classmethod
    def _validate_series_data(klass, s_data):
        """Ensures that the all necessary fields in ``s_data` are populated.

        ``s_data`` must include a valid ``frequency`` (which should always be
        ``weekly``), ``every`` (how many weeks between events in the series),
        and if the recurrence ends on a specific date, it should be defined,
        and if the recurrence ends after a specific number of occurrences, that
        number should be defined.

        :param dict s_data: The series data to validate.
        :raises: ValueError
        """

        if not (s_data['frequency'] and
                s_data['every'] and
                (s_data['ends_on'] and s_data['recurrence_end_date'] or
                 s_data['ends_after'] and s_data['num_occurrences'])):
            raise ValueError('Cannont create recurrence from series data.')

        if s_data['frequency'] != 'weekly':
            raise ValueError('Unknown frequency value "%s"' % s_data.frequency)

    @classmethod
    def _more_events(klass, series, date_data):
        """Returns True if more events exist in this series after ``date_data``.

        :Example:

        If the series included a recurrence for an event five times, and
        ``series.events`` contained only three events, this would return True.

        :Example:

        If the series started on Jan 1 and recurred weekly until Feb 1, and
        date_data represented Jan 29, this would return False, because the next
        event in the series would be after the end of the recurrence.

        :param series: The event series in question
        :type series: :class:`EventSeries`
        :param dict date_data: The reference date.

        :returns: True if there are more events in the series.
        :rtype: bool.
        """

        if (series.ends_after
                and len(series.events) >= series.num_occurrences
                or series.ends_on
                and date_data['start_date'] > series.recurrence_end_date):
            return False
        return True

    def _make_event(klass, e_data, d_data):
        """Create a new :class:`Event` object and save it to Mongoengine.

        The event is created by unpacking non-None fields of ``e_data`` and
        ``d_data`` in the constructor for :class:`Event`.

        :param dict e_data: The event data for this event.
        :param dict d_data: The date data for this event.
        """
        params = klass._remove_none_fields(dict(e_data.items() + d_data.items()))
        event = Event(**params)
        event.save()
        return event

    @classmethod
    def _make_series(klass, form, **kwargs):
        """Create a new :class:`EventSeries` object and save it to Mongoengine.

        The event is made by creating ``series_data`` and then unpacking it
        into the constructor for :class:`EventSeries`.

        :param form: The WTForm form to fetch series data from.
        :type form: :class:`CreateEventForm` or a subclass.
        :param dict kwargs: Any other arguments that should be applied on top
            of the form data.

        :returns: The newly created series.
        :rtype: :class:`EventSeries`
        """

        series_data = DataBuilder.series_data_from_form(form)
        series_data.update(kwargs)
        klass._validate_series_data(series_data)
        series_data = klass._remove_none_fields(series_data)

        series = EventSeries(**series_data)
        series.save()
        return series

    @classmethod
    def _update_event(klass, event, *data_dicts):
        """Updates ``event`` in Mongoengine using the dictionaries in
        ``data_dicts``.

        To update and overwrite using ``event.update(**d)``, ``d`` must have
        keys that begin with ``set__``.

        :Example:

        To change the title of an event, ``d`` must be
        ``{'set__title': 'New Title'}``.

        :param event: The event to update.
        :type event: :class:`Event`.
        :param data_dicts: The updates to apply to ``event``.
        :type data_dicts: list of dicts.
        """
        # Create d
        d = {}
        for data_dict in data_dicts:
            d.update(data_dict)
        d = klass._remove_none_fields(d)
        d = dict(("set__" + k, v) for k, v in d.iteritems())

        # Update and save.
        event.update(**d)
        event.save()

    @classmethod
    def _changes_are_easy(klass, event, series_data, date_data):
        """Returns True if the changes we want to make to event are easy to
        perform.

        Hard changes include changes to how the recurrence behaves and in start
        and end dates.

        :param event: The event we want to update.
        :type event: :class:`Event`.
        :param dict series_data: The desired recurrence behavior.
        :param dict date_data: The desired date for the event.
        """
        # Changes in how the recurrence behaves are hard.
        for k, v in series_data.iteritems():
            if getattr(event.parent_series, k) != v:
                return False

        # Changes in start and end dates are hard.
        for k, v in date_data.iteritems():
            if getattr(event, k) != v:
                return False

        # Changes are easy
        return True



class DataBuilder(object):
    """A class with helper functions that translate WTForms forms and
    Mongoengine objects to and from different dictionary shapes.

    These methods are used to create ``form_data``, ``event_data``,
    ``series_data``, and ``date_data``.
    """

    @classmethod
    def form_data_from_event(klass, event):
        """Translate an single :class:`Event` into a dictionary of form data.

        :param event: The event to translate.
        :type event: :class:`Event`

        :returns: Form data.
        :rtype: dict
        """

        return {
            'title': event.title,
            'slug': event.slug,
            'location': event.location,
            'start_date': event.start_date,
            'start_time': event.start_time,
            'end_date': event.end_date,
            'end_time': event.end_time,
            'published': event.published,
            'short_description': event.short_description_markdown,
            'long_description': event.long_description_markdown,
            'is_recurring': event.is_recurring,
            'facebook_url': event.facebook_url,
            'event_image': event.image.filename if event.image else None
        }

    @classmethod
    def form_data_from_series(klass, series):
        """Translate an :class:`EventSeries` into a dictionary of recurrence
        form data.

        :param series: The series to translate.
        :type series: :class:`EventSeries`

        :returns: Form data.
        :rtype: dict
        """
        return {
            'frequency': series.frequency,
            'every': series.every,
            'ends': 'on' if series.ends_on else 'after',
            'num_occurrences': series.num_occurrences,
            'recurrence_end_date': series.recurrence_end_date,
            'recurrence_summary': series.recurrence_summary
        }

    @classmethod
    def event_data_from_form(klass, form, creator=None):
        """Translate a :class:`~app.forms.CreateEventForm` or a subclass into a
        dictionary of event data.

        :param form: The form to translate.
        :type form: :class:`~app.forms.CreateEventForm` or a subclasss
        :param creator: The creator of the event.
        :type creator: :class:`~app.models.User`

        :returns: Event data.
        :rtype: dict
        """

        if not form:
            return {}
        event_image = None
        filename = form.event_image.data
        if filename and Image.objects(filename=filename).count() == 1:
            event_image = Image.objects().get(filename=filename)

        event_data =  {
            'title': form.title.data,
            'slug': form.slug.data,
            'location': form.location.data,
            'start_time': form.start_time.data,
            'end_time': form.end_time.data,
            'published': form.published.data,
            'short_description_markdown': form.short_description.data,
            'long_description_markdown': form.long_description.data,
            'is_recurring': form.is_recurring.data,
            'facebook_url': form.facebook_url.data,
            'image': event_image
        }
        if creator:
            event_data['creator'] = creator
        return event_data

    @classmethod
    def date_data_from_form(klass, form):
        """Translate a :class:`~app.forms.CreateEventForm` or a subclass into a
        dictionary of date data.

        :param form: The form to translate.
        :type form: :class:`~app.forms.CreateEventForm` or a subclasss

        :returns: Date data.
        :rtype: dict
        """

        if not form:
            return {}
        return {
            'start_date': form.start_date.data,
            'end_date': form.end_date.data,
        }

    @classmethod
    def series_data_from_form(klass, form):
        """Translate a :class:`~app.forms.CreateEventForm` or a subclass into a
        dictionary of series data.

        :param form: The form to translate.
        :type form: :class:`~app.forms.CreateEventForm` or a subclasss

        :returns: Series data.
        :rtype: dict
        """

        if not form:
            return {}
        return {
            'frequency': form.frequency.data,
            'every': form.every.data,
            'slug': form.slug.data,
            'ends_on': form.ends.data == 'on',
            'ends_after': form.ends.data == 'after',
            'num_occurrences': form.num_occurrences.data,
            'recurrence_end_date': form.recurrence_end_date.data,
            'recurrence_summary': form.recurrence_summary.data
        }

    @classmethod
    def event_and_date_data_from_form(klass, form, creator=None):
        """Translate a :class:`~app.forms.CreateEventForm` or a subclass into a
        dictionary of both event and date data.

        :param form: The form to translate.
        :type form: :class:`~app.forms.CreateEventForm` or a subclasss
        :param creator: The creator of the event.
        :type creator: :class:`~app.models.User`

        :returns: Event and date data.
        :rtype: dict
        """

        if not form:
            return {}
        event_data = klass.event_data_from_form(form, creator=creator)
        date_data = klass.date_data_from_form(form)
        return dict(event_data.items() + date_data.items())
