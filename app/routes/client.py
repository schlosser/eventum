from app import adi
import json
from flask import Blueprint, render_template, abort, redirect, url_for, request
from app.models import Event, BlogPost
from datetime import datetime, date, timedelta
from mongoengine import Q

client = Blueprint('client', __name__)

_resources = None
_faqs = None
_companies = None

@client.route('/')
def index():
    all_events = (Event.objects(
        Q(published=True,
          end_date__gt=date.today()) |
        Q(published=True,
          end_date=date.today(),
          end_time__gt=datetime.now().time())))
    events = all_events.order_by('start_date', 'start_time')[:4]

    all_blog_posts = BlogPost.objects(published=True).order_by('-date_published')
    blog_post = all_blog_posts[0] if all_blog_posts else None

    return render_template('index.html',
                           events=events,
                           blog_post=blog_post)

@client.route('/contact')
def contact():
    return render_template('contact.html')

@client.route('/jobfair')
def jobfair():
    force = request.args.get('force') is not None
    companies = _get_companies(force=force)
    return render_template('jobfair.html', companies=companies)

def _get_companies(force=False):
    global _companies
    if not _companies or force:
        with open(adi['COMPANIES_PATH']) as f:
            _companies = json.loads(f.read()).get('companies')
    return _companies

@client.route('/labs')
def labs():
    force = request.args.get('force') is not None
    faqs = _get_faqs(force=force)
    return render_template('labs.html', faqs=faqs)

def _get_faqs(force=False):
    global _faqs
    if not _faqs or force:
        with open(adi['FAQ_PATH']) as f:
            _faqs = json.loads(f.read()).get('questions')
    return _faqs

@client.route('/learn')
def learn():
    return redirect(url_for('.resources'))

@client.route('/resources')
def resources():
    force = request.args.get('force') is not None
    resources_data = _get_resources(force=force)
    return render_template('resources.html', resources=resources_data)

def _get_resources(force=False):
    global _resources
    if not _resources or force:
        with open(adi['RESOURCES_PATH']) as f:
            _resources = json.loads(f.read())
    return _resources


@client.route('/events')
def events():
    today = date.today()
    last_sunday = datetime.combine(today - timedelta(days=today.isoweekday()+7),
                                   datetime.min.time())
    next_sunday = datetime.combine(today + timedelta(days=7-today.isoweekday()),
                                   datetime.min.time())
    recent_and_upcoming = Event.objects(published=True,
                                        start_date__gt=last_sunday).order_by('start_date',
                                                                             'start_time')

    recent_events = recent_and_upcoming.filter(end_date__lt=today)

    events_this_week = recent_and_upcoming.filter(end_date__gte=today,
                                                  start_date__lt=next_sunday)

    upcoming_events = recent_and_upcoming.filter(start_date__gt=next_sunday)[:4]

    more_past_events = bool(Event.objects(published=True,
                                          start_date__lte=last_sunday).count())

    return render_template('events/events.html',
                           recent_events=recent_events,
                           events_this_week=events_this_week,
                           upcoming_events=upcoming_events,
                           more_past_events=more_past_events)

@client.route('/events/<int:index>')
def event_archive(index):
    index = int(index)
    if index <= 0:
        return redirect(url_for('.events'))

    today = date.today()
    last_sunday = datetime.combine(today - timedelta(days=today.weekday()+7),
                                   datetime.min.time())

    past_events=Event.objects(published=True,
                              start_date__lt=last_sunday).order_by('start_date')

    if not past_events:
        return redirect(url_for('.events'))

    previous_index = index - 1
    next_index = index + 1 if len(past_events) > 10*index else None
    return render_template('events/archive.html',
                           events=past_events[10*(index-1):10*(index)],
                           previous_index=previous_index,
                           next_index=next_index)

@client.route('/events/<slug>')
def event(slug):
    if Event.objects(published=True, slug=slug).count() == 0:
        abort(404) # Either invalid event ID or duplicate IDs.

    event = Event.objects(published=True, slug=slug)[0]


    if event.is_recurring:
        upcoming_event_instances = Event.objects(published=True,
                                                 start_date__gte=date.today(),
                                                 slug=slug).order_by('start_date')
        if upcoming_event_instances:
            event = upcoming_event_instances[0]
        else:
            event = event.parent_series.events[-1]

        upcoming_events = Event.objects(published=True,
                                        start_date__gte=date.today(),
                                        id__ne=event.id).order_by('start_date')[:3]


        return render_template('events/event.html',
                               event=event,
                               upcoming_events=upcoming_events)

    upcoming_events = Event.objects(published=True,
                                    start_date__gte=date.today(),
                                    id__ne=event.id).order_by('start_date')[:3]

    return render_template('events/event.html',
                           event=event,
                           upcoming_events=upcoming_events)

@client.route('/events/<slug>/<index>')
def recurring_event(slug, index):
    if Event.objects(published=True, slug=slug).count() == 0:
        abort(404) # Either invalid event ID or duplicate IDs.

    index = int(index)

    event = Event.objects(published=True, slug=slug)[0]

    upcoming_events = Event.objects(published=True,
                                    start_date__gte=date.today(),
                                    id__ne=event.id).order_by('start_date')[:3]


    if not event.is_recurring or not event.parent_series:
        return redirect(url_for('.event', slug=slug))

    if len(event.parent_series.events) <= index:
      abort(404)

    event = event.parent_series.events[index]
    return render_template('events/event.html',
                           event=event,
                           upcoming_events=upcoming_events)
