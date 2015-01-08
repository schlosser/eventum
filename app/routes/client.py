"""
.. module:: client
    :synopsis: All routes on the ``client`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app import adi
import json
from flask import Blueprint, render_template, abort, redirect, url_for, request
from app.models import Event, BlogPost
from datetime import datetime, date, timedelta
from mongoengine import Q

client = Blueprint('client', __name__)

_resources = None
_labs_data = None
_companies = None

@client.route('/', methods=['GET'])
def index():
    """View the ADI homepage.

    **Route:** ``/``

    **Methods:** ``GET``
    """

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

@client.route('/contact', methods=['GET'])
def contact():
    """View contact information.

    **Route:** ``/contact``

    **Methods:** ``GET``
    """
    return render_template('contact.html')

@client.route('/feedback', methods=['GET'])
def feedback():
    """Submit feedback on past ADI events.

    **Route:** ``/feedback``

    **Methods:** ``GET``
    """
    return render_template('feedback.html')

@client.route('/jobfair', methods=['GET'])
def jobfair():
    """View the ADI Startup Career Fair page.

    **Route:** ``/jobfair``

    **Methods:** ``GET``
    """
    force = request.args.get('force') is not None
    companies = _get_companies(force=force)
    return render_template('jobfair.html', companies=companies)

def _get_companies(force=False):
    global _companies
    if not _companies or force:
        with open(adi['COMPANIES_PATH']) as f:
            _companies = json.loads(f.read()).get('companies')
    return _companies

@client.route('/labs', methods=['GET'])
def labs():
    """View information about ADI Labs

    **Route:** ``/labs``

    **Methods:** ``GET``
    """
    force = request.args.get('force') is not None
    labs_data = _get_labs_data(force=force)
    return render_template('labs.html', data=labs_data)

def _get_labs_data(force=False):
    global _labs_data
    if not _labs_data or force:
        with open(adi['LABS_DATA_PATH']) as f:
            _labs_data = json.loads(f.read())
    return _labs_data

@client.route('/learn', methods=['GET'])
def learn():
    """Alias for :func:`resources`.

    **Route:** ``/learn``

    **Methods:** ``GET``
    """
    return redirect(url_for('.resources'))

@client.route('/resources', methods=['GET'])
def resources():
    """Learn to code! View resources for learning how to program different
    websites.

    **Route:** ``/resources``

    **Methods:** ``GET``
    """
    force = request.args.get('force') is not None
    resources_data = _get_resources(force=force)
    return render_template('resources.html', resources=resources_data)

def _get_resources(force=False):
    global _resources
    if not _resources or force:
        with open(adi['RESOURCES_PATH']) as f:
            _resources = json.loads(f.read())
    return _resources

@client.route('/events', methods=['GET'])
def events():
    """View the latest events.

    **Route:** ``/events``

    **Methods:** ``GET``
    """
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

@client.route('/events/<int:index>', methods=['GET'])
def event_archive(index):
    """View old events.

    **Route:** ``/events/<index>``

    **Methods:** ``GET``

    :param int index: The page to fetch
    """
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

@client.route('/events/<slug>', methods=['GET'])
def event(slug):
    """View a specific non-recurring event, or the next upcoming instance of
    a recurring event.

    **Route:** ``/events/<slug>``

    **Methods:** ``GET``

    :param str slug: The unique slug ID for the post.
    """
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

@client.route('/events/<slug>/<index>', methods=['GET'])
def recurring_event(slug, index):
    """View a specific instance of a recurring event.

    **Route:** ``/events/<slug>/<index>``

    **Methods:** ``GET``

    :param str slug: The unique slug ID for the post.
    :param int index: The instance of the event to fetch.
    """
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
