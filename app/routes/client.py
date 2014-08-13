from flask import Blueprint, render_template, abort, redirect, url_for
from app.models import Event
from datetime import datetime

client = Blueprint('client', __name__)

@client.route('/')
def index():
    return render_template('index.html', events=Event.objects())

@client.route('/events')
def events():
    return render_template('events/events.html', events=Event.objects())

@client.route('/events/<slug>')
def event(slug):
    if Event.objects(slug=slug).count() == 0:
        abort(404) # Either invalid event ID or duplicate IDs.

    event = Event.objects(slug=slug)[0]

    if event.is_recurring:
        upcoming_event_instances = Event.objects(start_time__gt=datetime.now())
        if upcoming_event_instances:
            event = upcoming_event_instances[0]
        else:
            event = event.parent_series.events[-1]


    return render_template('events/event.html', event=event)

@client.route('/events/<slug>/<index>')
def recurring_event(slug, index):
    if Event.objects(slug=slug).count() == 0:
        abort(404) # Either invalid event ID or duplicate IDs.

    event = Event.objects(slug=slug)[0]

    if not event.is_recurring or not event.parent_series:
        return redirect(url_for('.event', slug=slug))

    event = event.parent_series.events[index]

    return render_template('events/event.html', event=event)
