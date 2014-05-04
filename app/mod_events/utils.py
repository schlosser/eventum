from app.mod_events.models import Event
from app.mod_events.forms import CreateEventForm

def create_event(form, event=None, **kwargs):
    """"""
    event_data = {
        "title": form.title.data,
        "location":form.location.data,
        "start_date":form.start_date.data,
        "start_time":form.start_time.data,
        "end_date":form.end_date.data,
        "end_time":form.end_time.data,
        "published":False,
        "descriptions": {
            "short": form.short_description.data,
            "long": form.long_description.data
            }
        }
    if kwargs:
        event_data.update(kwargs)

    event_data = remove_none_fields(event_data)

    if event:
        event_data = dict(("set__"+k,v) for k,v in event_data.iteritems())
        event.update(**event_data)
        return event
    return Event(**event_data)

def create_form(event, request):
    """"""
    form_data = {
        "title":event.title,
        "location":event.location,
        "start_date":event.start_date,
        "start_time":event.start_time,
        "end_date":event.end_date,
        "end_time":event.end_time,
        "published":event.published,
        "short_description":event.descriptions['short'],
        "long_description":event.descriptions['long']
    }
    form_data = remove_none_fields(form_data)
    return CreateEventForm(request.form, **form_data)

def remove_none_fields(d):
    """"""
    return dict((k,v) for k,v in d.iteritems() if v is not None)