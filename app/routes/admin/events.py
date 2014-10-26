from datetime import datetime, timedelta, date

from flask import Blueprint, request, render_template, g, redirect, \
    url_for, flash, jsonify

from bson.objectid import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError

from app.models import Event, Image
from app.forms import CreateEventForm, EditEventForm, DeleteEventForm, UploadImageForm
from app.lib.decorators import login_required, requires_privilege, development_only

from app.lib.error import GoogleCalendarAPIError
from app.lib.events import EventsHelper
events = Blueprint('events', __name__)

@events.route('/events')
@login_required
def index():
    """View the events for this and next week, with optional future and past
    events.

    **Route:** `/admin/events`
    """

    past = int(request.args.get('past')) if request.args.get('past') else 0
    future = int(request.args.get('future')) if request.args.get('future') else 0

    past_events, this_week, next_week, future_events = \
    _get_events_for_template(past, future)

    return render_template('admin/events/events.html',
                           past_events=past_events,
                           this_week=this_week,
                           next_week=next_week,
                           future_events=future_events)

def _format_for_display(dt):
    """Formats `dt` like "Saturday, October 25".

    :param dt: The datetime to fomat.
    :type dt: :class:`datetime.datetime`.

    :returns: The formatted date.
    :rtype: str
    """
    # Cast the %d part to int and back so that 06 --> 6
    return dt.strftime("%A, %B ") + str(int(dt.strftime("%d")))

def _get_events_for_template(past, future):
    """Returns the events to insert in the events template.  Forms four lists
    of dates"""
    today = date.today()
    last_sunday = datetime.combine(today - timedelta(days=(today.isoweekday() % 7)),
                                   datetime.min.time())
    next_sunday = last_sunday + timedelta(days=7)
    following_sunday = last_sunday + timedelta(days=14)

    this_week = Event.objects(start_date__gte=last_sunday,
                              start_date__lt=next_sunday).order_by('start_date')
    next_week = Event.objects(start_date__gte=next_sunday,
                              start_date__lt=following_sunday).order_by('start_date')
    past_events = []
    future_events = []

    for week_no in range(past):
        ending_sunday = last_sunday - timedelta(days=7 * week_no)
        starting_sunday = last_sunday - timedelta(days=7 * (week_no + 1))
        week_name = _format_for_display(starting_sunday)
        events = Event.objects(start_date__gte=starting_sunday,
                               start_date__lt=ending_sunday)
        past_events.insert(0, {
            'week_name': week_name,
            'events': events,
        })

    for week_no in range(future):
        starting_sunday = following_sunday + timedelta(days=7 * week_no)
        ending_sunday = following_sunday + timedelta(days=7 * (week_no + 1))
        week_name = _format_for_display(starting_sunday)
        events = Event.objects(start_date__gte=starting_sunday,
                               start_date__lt=ending_sunday)
        future_events.append({
            'week_name': week_name,
            'events': events,
        })

    return past_events, this_week, next_week, future_events

@events.route('/events/create', methods=['GET', 'POST'])
@requires_privilege('edit')
def create():
    """"""
    form = CreateEventForm(request.form)
    if form.validate_on_submit():
        try:
            EventsHelper.create_event(form, g.user)
        except GoogleCalendarAPIError as e:
            flash(e.message)

        return redirect(url_for('.index'))
    if form.errors:
        for error in form.errors:
            for message in form.errors[error]:
                flash(message)

    upload_form = UploadImageForm()
    delete_form = DeleteEventForm()
    images = Image.objects()
    return render_template('admin/events/create.html', form=form,
                           delete_form=delete_form, upload_form=upload_form,
                           images=images)

@events.route('/events/edit/<event_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit(event_id):
    """"""
    try:
        event = Event.objects().get(id=event_id)
    except (DoesNotExist, ValidationError):
        flash('Cannont find event with id "%s"' % event_id)
        return redirect(url_for('.index'))

    form = EditEventForm(request.form) if request.method == 'POST' else \
        EventsHelper.create_form(event, request)

    if form.validate_on_submit():
        try:
            EventsHelper.update_event(event, form)
        except GoogleCalendarAPIError as e:
            flash(e.message)

        return redirect(url_for('.index'))
    if form.errors:
        for error in form.errors:
            for message in form.errors[error]:
                flash(message)

    delete_form = DeleteEventForm()
    upload_form = UploadImageForm()
    images = Image.objects()

    return render_template('admin/events/edit.html', form=form, event=event,
                           delete_form=delete_form, upload_form=upload_form,
                           images=images)

@events.route('/events/delete/<event_id>', methods=['POST'])
@requires_privilege('edit')
def delete(event_id):
    """"""
    object_id = ObjectId(event_id)
    form = DeleteEventForm(request.form)
    if Event.objects(id=object_id).count() == 1:
        event = Event.objects().with_id(object_id)
        try:
            EventsHelper.delete_event(event, form)
        except GoogleCalendarAPIError as e:
            flash(e.message)
    else:
        flash('Invalid event id')
    return redirect(url_for('.index'))

def set_published_status(event_id, status):
    """"""
    object_id = ObjectId(event_id)
    if Event.objects(id=object_id).count() == 1:
        event = Event.objects().with_id(object_id)
        if status != event.published:
            event.published = status
            # TODO Actually publish/unpublish the event here
            if event.published:
                event.date_published = datetime.now()
                flash('Event published')
            else:
                event.date_published = None
                flash('Event unpublished')
            event.save()
        else:
            flash("The event had not been published.  No changes made.")
    else:
        flash('Invalid event id')
    return redirect(url_for('.index'))

@events.route('/events/publish/<event_id>', methods=['POST'])
@requires_privilege('publish')
def publish(event_id):
    """"""
    return set_published_status(event_id, True)

@events.route('/events/unpublish/<event_id>', methods=['POST'])
@requires_privilege('publish')
def unpublish(event_id):
    """"""
    return set_published_status(event_id, False)

@events.route('/events/view')
@requires_privilege('edit')
@development_only
def view():
    return str(Event.objects())

@events.route('/events/wipe')
@development_only
def mom():
    for e in Event.objects():
        e.delete()
    return "hi"
