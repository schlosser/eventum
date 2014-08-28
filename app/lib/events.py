from app.models import Event, EventSeries, Image
from app.forms import CreateEventForm
from datetime import timedelta
from app import gcal_client
from app.lib.error import GoogleCalendarAPIMissingID


class EventsHelper(object):

    PUBLIC = 'public'
    PRIVATE = 'private'

    @classmethod
    def create_form(klass, event, request):
        """"""
        form_data = DataBuilder.form_data_from_event(event)
        if event.parent_series:
            updates = DataBuilder.form_data_from_series(event.parent_series)
            form_data.update(updates)
        form_data = klass._remove_none_fields(form_data)
        return CreateEventForm(request.form, **form_data)

    @classmethod
    def create_event(klass, form, creator):
        """"""
        if form.is_recurring.data:
            # Series
            return klass.create_series(form, creator)
        # Single event
        return klass.create_single_event(form, creator)

    @classmethod
    def update_event(klass, event, form):
        """"""
        # Determine if the event should be moved between calendars
        move_to = None
        if event.is_published != form.is_published.data:
            move_to = klass.PUBLIC if form.is_published.data else klass.PRIVATE

        if event.is_recurring != form.is_recurring.data:
            if event.is_recurring:
                # Series -> single event
                return klass.convert_to_single_event(event, form, move_to=move_to)
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
        """"""
        if event.is_recurring:
            if form.delete_all.data:
                # Series
                return klass.delete_series(event)
            # Single event from series
            return klass.delete_single_event_from_series(event)
        # Single event
        return klass.delete_single_event(event)

    @classmethod
    def create_single_event(klass, form, creator):
        """"""
        # Generate the event and date data
        event_and_date_data = DataBuilder.event_and_date_data_from_form(form, creator=creator)
        event_and_date_data = klass._remove_none_fields(event_and_date_data)

        event = Event(**event_and_date_data)
        event.save()

        # Return the Google Calendar response
        return gcal_client.create_event(event)

    @classmethod
    def create_series(klass, form, creator):
        """"""
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
        """"""
        event_and_date_data = DataBuilder.event_and_date_data_from_form(form)
        event_and_date_data = klass._remove_none_fields(event_and_date_data)
        klass._update_event(event, event_and_date_data)

        # Update the event and publish it as necessary
        if move_to == klass.PUBLIC:
            response = gcal_client.publish_event(event)
        elif move_to == klass.PRIVATE:
            response = gcal_client.unpublish_event(event)
        response = gcal_client.update_event(event)

        # Return the Google Calendar response
        return response

    @classmethod
    def update_series(klass, event, form, move_to=None):
        """"""
        event_data = DataBuilder.event_data_from_form(form)
        date_data = DataBuilder.date_data_from_form(form)

        # Make the parent series
        series_data = DataBuilder.series_data_from_form(form)
        klass._validate_series_data(series_data)

        if klass._changes_are_easy(event, series_data, date_data):
            for e in event.parent_series.events:
                # the date data isn't changing, so pass in {}
                klass._update_event(e, event_data, {})
            series = event.parent_series
        else:
            shared_gcal_id = event.gcal_id
            shared_gcal_sequence = event.gcal_sequence
            shared_creator = event.creator

            event.parent_series.delete_all()
            series = klass._make_series(None, gcal_id=shared_gcal_id, **series_data)

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

        if move_to == klass.PUBLIC:
            response = gcal_client.publish_event(series.events[0])
        elif move_to == klass.PRIVATE:
            response = gcal_client.unpublish_event(series.events[0])
        response = gcal_client.update_event(series.events[0])
        return response

    @classmethod
    def update_single_event_from_series(klass, event, form):
        """"""
        event_and_date_data = DataBuilder.event_and_date_data_from_form(form)
        event_and_date_data = klass._remove_none_fields(event_and_date_data)
        klass._update_event(event, event_and_date_data)

        # Return Google Calendar response
        return gcal_client.update_event(event, as_exception=True)

    @classmethod
    def convert_to_series(klass, event, form, move_to=None):
        """"""
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
        """"""
        event_data = DataBuilder.event_data_from_form(form)
        date_data = DataBuilder.date_data_from_form(form)

        event.parent_series.delete_all_except(event)
        klass._update_event(event, date_data, event_data)

        # Delete the series and create a single event
        return gcal_client.update_event(event)


    @classmethod
    def delete_single_event(klass, event):
        """"""
        try:
            response = gcal_client.delete_event(event)
        except GoogleCalendarAPIMissingID:
            response = None
        event.delete()

        # Return the Google Calendar response
        return response

    @classmethod
    def delete_single_event_from_series(klass, event):
        """"""
        # Cancel the series on Google Calendar
        try:
            response = gcal_client.delete_event(event, as_exception=True)
        except GoogleCalendarAPIMissingID:
            response = None

        # Delete the one event
        event.parent_series.delete_one(event)

        # Return the Google Calendar response
        return response

    @classmethod
    def delete_series(klass, event):
        """"""
        # Delete the series
        try:
            response = gcal_client.delete_event(event)
        except GoogleCalendarAPIMissingID:
            response = None
        event.parent_series.delete_all()

        # Return the Google Calendar response
        return response

    @classmethod
    def _remove_none_fields(klass, d):
        """"""
        return dict((k, v) for k, v in d.iteritems() if v is not None)

    @classmethod
    def _increment_date_data(klass, series, date_data):
        """"""
        # delta is the timedelta in between events
        delta = timedelta(days=7 * series.every)
        date_data['start_date'] = date_data['start_date'] + delta
        date_data['end_date'] = date_data['end_date'] + delta

    @classmethod
    def _validate_series_data(klass, s_data):
        """"""
        if not (s_data['frequency'] and
                s_data['every'] and
                (s_data['ends_on'] and s_data['recurrence_end_date'] or
                 s_data['ends_after'] and s_data['num_occurances'])):
            raise ValueError('Cannont create recurrence from series data.')

        if s_data['frequency'] != 'weekly':
            raise ValueError('Unknown frequency value "%s"' % s_data.frequency)

    @classmethod
    def _more_events(klass, series, date_data):
        """"""
        if (series.ends_after and len(series.events) >= series.num_occurances or
            series.ends_on and date_data['start_date'] > series.recurrence_end_date):
            return False
        return True

    @classmethod
    def _make_event(klass, e_data, d_data):
        """"""
        params = klass._remove_none_fields(dict(e_data.items() + d_data.items()))
        event = Event(**params)
        event.save()
        return event

    @classmethod
    def _make_series(klass, form, **kwargs):
        series_data = DataBuilder.series_data_from_form(form)
        series_data.update(kwargs)
        klass._validate_series_data(series_data)
        series_data = klass._remove_none_fields(series_data)

        series = EventSeries(**series_data)
        series.save()
        return series

    @classmethod
    def _update_event(klass, event, *data_dicts):
        """"""
        d = {}
        for data_dict in data_dicts:
            d.update(data_dict)
        d = klass._remove_none_fields(d)
        d = dict(("set__" + k, v) for k, v in d.iteritems())
        event.update(**d)
        event.save()

    @classmethod
    def _changes_are_easy(klass, event, series_data, date_data):
        """"""
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

    @classmethod
    def form_data_from_event(klass, event):
        return {
            'title': event.title,
            'slug': event.slug,
            'location': event.location,
            'start_date': event.start_date,
            'start_time': event.start_time,
            'end_date': event.end_date,
            'end_time': event.end_time,
            'is_published': event.is_published,
            'short_description': event.short_description_markdown,
            'long_description': event.long_description_markdown,
            'is_recurring': event.is_recurring,
            'facebook_url': event.facebook_url,
            'event_image': event.image.filename if event.image else None
        }

    @classmethod
    def form_data_from_series(klass, series):
        return {
            'frequency': series.frequency,
            'every': series.every,
            'ends': 'on' if series.ends_on else 'after',
            'num_occurances': series.num_occurances,
            'recurrence_end_date': series.recurrence_end_date,
            'recurrence_summary': series.recurrence_summary
        }

    @classmethod
    def event_data_from_form(klass, form, creator=None):
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
            'is_published': form.is_published.data,
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
        if not form:
            return {}
        return {
            'start_date': form.start_date.data,
            'end_date': form.end_date.data,
        }

    @classmethod
    def series_data_from_form(klass, form):
        if not form:
            return {}
        return {
            'frequency': form.frequency.data,
            'every': form.every.data,
            'slug': form.slug.data,
            'ends_on': form.ends.data == 'on',
            'ends_after': form.ends.data == 'after',
            'num_occurances': form.num_occurances.data,
            'recurrence_end_date': form.recurrence_end_date.data,
            'recurrence_summary': form.recurrence_summary.data
        }

    @classmethod
    def event_and_date_data_from_form(klass, form, creator=None):
        if not form:
            return {}
        event_data = klass.event_data_from_form(form, creator=creator)
        date_data = klass.date_data_from_form(form)
        return dict(event_data.items() + date_data.items())

