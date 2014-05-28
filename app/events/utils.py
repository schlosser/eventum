from app.events.models import Event
from app.events.forms import CreateEventForm
from datetime import timedelta

def create_event(form, event=None, update_all=False, update_following=False,
                 **kwargs):
    """"""
    event_data = {
        "title": form.title.data,
        "location": form.location.data,
        "start_date": form.start_date.data,
        "start_time": form.start_time.data,
        "end_date": form.end_date.data,
        "end_time": form.end_time.data,
        "published": form.published.data,
        "descriptions": {
            "short": form.short_description.data,
            "long": form.long_description.data
        },
        "repeat": form.repeat.data,
        "frequency": form.frequency.data,
        "every": form.every.data,
        "ends": form.ends.data,
        "num_occurances": form.num_occurances.data,
        "repeat_end_date": form.repeat_end_date.data,
        "summary": form.summary.data
    }
    if kwargs:
        event_data.update(kwargs)

    # Create and save a new event if this is not an update
    if not event:
        event = create_and_save(event_data)
        event.root_event = event
        event.save()
        create_series(event, event_data)
        return

    # If this is not a recurring event, we simply update this event and return
    if not event.repeat:
        for e in event.event_series:
            e.delete()
        update_and_save(event, event_data)
        return

    event_data['root_event'] = event
    event_data['creator'] = event.creator

    # Isolate only propeties that will be changed
    changes = set([k for k,v in event_data.iteritems() if getattr(event,k)==v])

    simple_changes = set(["title", "location", "start_date", "start_time",
                      "end_date", "end_time", "published", "descriptions"])
    multiple_only = set(["repeat", "frequency", "every", "ends",
                         "num_occurances", "repeat_end_date", "summary"])
    if form.update_all:
        # If all the changes are easy, do the changes to the current objects
        if changes.issubset(simple_changes):
            for e in event.event_series + [event]:
                update_and_save(e, event_data)
        else:
            # Otherwise, delete all the related events and remake them
            print "root event: ", event.root_event
            root_event = event.root_event if event.root_event else event
            for e in root_event.event_series:
                e.delete()
            event_data['root_event'] = root_event
            update_and_save(root_event, event_data)
            create_series(root_event, event_data)

    elif form.update_following:
        # If all the changes are easy, do the changes to the current objects
        if all([k in simple_changes for k in changes.keys()]):
            for e in event.event_series + [event]:
                if e.start_datetime() >= event.start_datetime():
                    update_and_save(e, event_data)
        else:
            # Otherwise delete all following events, treat the current event as
            # a root event, and make a new series.
            for e in event.event_series:
                if e.start_datetime() > event.start_datetime():
                    e.delete()
            update_and_save(event, event_data)
            create_series(event, event_data)

    else:
        # Don't change the repeat settings for a single event (why would
        # someone do that?)
        for field in multiple_only:
            del event_data[field]
        update_and_save(event, event_data)


def update_event(event, form, update_all=False, update_following=False,
                 **kwargs):
    """"""
    create_event(form, event=event, update_all=update_all,
                 update_following=update_following, **kwargs)


def create_form(event, request):
    """"""
    form_data = {
        "title": event.title,
        "location": event.location,
        "start_date": event.start_date,
        "start_time": event.start_time,
        "end_date": event.end_date,
        "end_time": event.end_time,
        "published": event.published,
        "short_description": event.descriptions['short'],
        "long_description": event.descriptions['long'],
        "repeat": event.repeat,
        "frequency": event.frequency,
        "every": event.every,
        "ends": event.ends,
        "num_occurances": event.num_occurances,
        "repeat_end_date": event.repeat_end_date,
        "summary": event.summary
    }
    form_data = remove_none_fields(form_data)
    return CreateEventForm(request.form, **form_data)


def create_series(event, data):
    """"""
    def increment_dates(data, delta):
        """"""
        data['start_date'] = data['start_date'] + delta
        data['end_date'] = data['end_date'] + delta

    # Only make the series if all of the necesary fields are valid
    if not event.repeat or not event.frequency or not event.ends or \
        event.ends == "on" and not event.repeat_end_date or \
            event.ends == "after" and not event.num_occurances:
        return

    if event.frequency == "weekly":
        delta = timedelta(days=7*event.every)
    else:
        raise ValueError('Unknown frequency value "%s"' % event.frequency)
    increment_dates(data, delta)

    events = [event]
    while event.ends == "after" and len(events) < event.num_occurances or \
            event.ends == "on" and data['start_date'] <= event.repeat_end_date:
        e = create_and_save(data)
        increment_dates(data, delta)
        events.append(e)

    for e in events:
        e.event_series = events
        e.event_series.remove(e)
        e.save()

    print events


def update_and_save(event, d):
    """"""
    d = remove_none_fields(d)
    d = dict(("set__" + k, v) for k, v in d.iteritems())
    event.update(**d)
    event.save()


def create_and_save(d):
    """"""
    d = remove_none_fields(d)
    event = Event(**d)
    event.save()
    return event

def remove_none_fields(d):
    """"""
    return dict((k, v) for k, v in d.iteritems() if v is not None)
