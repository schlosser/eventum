from app.events.models import Event, EventSeries
from app.events.forms import CreateEventForm
from datetime import timedelta


def update_event(event, form, update_all=False, update_following=False,
                 **kwargs):
    """"""
    create_event(form, event=event, update_all=update_all,
                 update_following=update_following, **kwargs)


def create_event(form, event=None, update_all=False, update_following=False,
                 **kwargs):
    """"""
    event_data = {
        "title": form.title.data,
        "location": form.location.data,
        "start_time": form.start_time.data,
        "end_time": form.end_time.data,
        "is_published": form.is_published.data,
        "short_description": form.short_description.data,
        "long_description": form.long_description.data,
        "is_recurring": form.is_recurring.data,
    }
    date_data = {
        "start_date": form.start_date.data,
        "end_date": form.end_date.data,
    }
    recurrence_data = {
        "frequency": form.frequency.data,
        "every": form.every.data,
        "ends_on": form.ends.data == 'on',
        "ends_after": form.ends.data == 'after',
        "num_occurances": form.num_occurances.data,
        "recurrence_end_date": form.recurrence_end_date.data,
        "recurrence_summary": form.recurrence_summary.data
    } if form.is_recurring.data else None

    if kwargs:
        event_data.update(kwargs)
    if event:
        event_data['creator'] = event.creator

    # Create and save a new event / series if this is not an update
    if not event:
        create_series(event_data, date_data, recurrence_data)
        return

    # If this is no longer a recurring event, delete others and update this one
    if event.is_recurring and not form.is_recurring.data:
        event.parent_series.delete_all_except(event)
        update_and_save(event, date_data, event_data)
        return

    # If the recurrence is being added for the first time.
    if not event.is_recurring and form.is_recurring.data:
        create_series(event_data, date_data, recurrence_data, event=event)
        return

    recurrence_changes = event.parent_series and \
        any([k for k, v in recurrence_data.iteritems()
             if getattr(event.parent_series, k) != v]) or \
        any([k for k,v in date_data.iteritems() if getattr(event, k) != v])

    if form.update_all.data:
        # If all the changes are easy, do the changes to the current objects
        if not recurrence_changes:
            for e in event.parent_series.events:
                update_and_save(e, event_data, {})
        else:
            # Otherwise, delete all the related events and remake them
            event.parent_series.delete_all()
            create_series(event_data, date_data, recurrence_data)

    elif form.update_following.data:
        # If all the changes are easy, do the changes to the current objects
        if not recurrence_changes:
            for e in event.parent_series.events:
                if e.start_datetime() >= event.start_datetime():
                    update_and_save(e, event_data, {})
        else:
            # Otherwise delete all following events, treat the current event as
            # a root event, and make a new series.
            event.parent_series.delete_following(event)
            event.parent_series.delete()
            create_series(event_data, date_data, recurrence_data)

    else:
        # Only update changes to the event data
        update_and_save(event, event_data, date_data)


def create_form(event, request):
    """"""
    form_data = {
        "title": event.title,
        "location": event.location,
        "start_date": event.start_date,
        "start_time": event.start_time,
        "end_date": event.end_date,
        "end_time": event.end_time,
        "is_published": event.is_published,
        "short_description": event.short_description,
        "long_description": event.long_description,
        "is_recurring": event.is_recurring
    }
    if event.parent_series:
        form_data.update({
            "frequency": event.parent_series.frequency,
            "every": event.parent_series.every,
            "ends": "on" if event.parent_series.ends_on else "after",
            "num_occurances": event.parent_series.num_occurances,
            "recurrence_end_date": event.parent_series.recurrence_end_date,
            "recurrence_summary": event.parent_series.recurrence_summary
        })
        print "aloha"
        print form_data['recurrence_end_date']
    form_data = remove_none_fields(form_data)
    return CreateEventForm(request.form, **form_data)


def create_series(e_data, d_data, r_data, event=None):
    """"""
    def increment_dates(data, delta):
        """"""
        data['start_date'] = data['start_date'] + delta
        data['end_date'] = data['end_date'] + delta

    if not e_data['is_recurring']:
        make_event(e_data, d_data)
        return

    # Only make the series if all of the necesary fields are valid
    if not r_data['frequency'] or \
        r_data['ends_on'] and not r_data['recurrence_end_date'] or \
            r_data['ends_after'] and not r_data['num_occurances']:
        return

    if r_data['frequency'] == "weekly":
        delta = timedelta(days=7 * r_data['every'])
    else:
        raise ValueError('Unknown frequency value "%s"' % r_data.frequency)

    series = make_series(r_data)
    e_data['parent_series'] = series

    if event:
        update_and_save(event, e_data, d_data)
        series.events.append(event)
        increment_dates(d_data, delta)

    while r_data['ends_after'] and \
            len(series.events) < r_data['num_occurances'] or \
            r_data['ends_on'] and \
            d_data['start_date'] <= r_data['recurrence_end_date']:
        e = make_event(e_data, d_data)
        series.events.append(e)
        increment_dates(d_data, delta)

    series.save()


def update_and_save(event, e_data, d_data):
    """"""
    d = remove_none_fields(dict(e_data.items() + d_data.items()))
    d = dict(("set__" + k, v) for k, v in d.iteritems())
    event.update(**d)
    event.save()


def make_event(e_data, d_data):
    """"""
    d = remove_none_fields(dict(e_data.items() + d_data.items()))
    event = Event(**d)
    event.save()
    return event


def make_series(r_data):
    """"""
    d = remove_none_fields(r_data)
    series = EventSeries(**d)
    series.save()
    return series


def remove_none_fields(d):
    """"""
    return dict((k, v) for k, v in d.iteritems() if v is not None)
