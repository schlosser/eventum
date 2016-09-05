
"""
.. module:: events
    :synopsis: All routes on the ``events`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from datetime import datetime, timedelta, date

from flask import (Blueprint, request, render_template, g, redirect,
                   url_for, flash)

from bson.objectid import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError

from eventum.models import Event, Image
from eventum.forms import (CreateEventForm, EditEventForm, DeleteEventForm,
                           UploadImageForm)
from eventum.lib.decorators import login_required, requires_privilege
from eventum.routes.base import ERROR_FLASH, MESSAGE_FLASH

from eventum.lib.error import EventumError
from eventum.lib.events import EventsHelper
events = Blueprint('events', __name__)


@events.route('/events', methods=['GET'])
@login_required
def index():
    """View the events for this and next week, with optional future and past
    events.

    **Route:** ``/admin/events``

    **Methods:** ``GET``
    """
    past = request.args.get('past')
    future = request.args.get('future')
    past = int(past) if past else 0
    future = int(future) if future else 0

    (past_events,
     this_week,
     next_week,
     future_events) = _get_events_for_template(past, future)

    return render_template('eventum_events/events.html',
                           past_events=past_events,
                           this_week=this_week,
                           next_week=next_week,
                           future_events=future_events)


def _format_for_display(dt):
    """Formats ``dt`` like "Saturday, October 25".

    :param dt: The datetime to fomat.
    :type dt: :class:``datetime.datetime``.

    :returns: The formatted date.
    :rtype: str
    """
    # Cast the %d part to int and back so that 06 --> 6
    return dt.strftime("%A, %B ") + str(int(dt.strftime("%d")))


def _get_events_for_template(past, future):
    """Returns the events to insert in the events template.  Returns four
    groups of dates:

    - ``past_events``: A list of dictionaries, where the dictionaries contain a
        list of events for a week, and a label for the week.
    - ``this_week``: A list of events happening this week.
    - ``next_week``: A list of events happening next week.
    - ``future_events``: A list of dictionaries similar to ``post_events``,
        but for events happening in the future.

    :returns: ``past_events``, ``this_week``, ``next_week``, ``future_events``
    """
    today = date.today()
    last_sunday = datetime.combine(
        today - timedelta(days=(today.isoweekday() % 7)),
        datetime.min.time()
    )
    next_sunday = last_sunday + timedelta(days=7)
    following_sunday = last_sunday + timedelta(days=14)

    this_week = (Event.objects(start_date__gte=last_sunday,
                               start_date__lt=next_sunday)
                 .order_by('start_date'))
    next_week = (Event.objects(start_date__gte=next_sunday,
                               start_date__lt=following_sunday)
                 .order_by('start_date'))
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
    """Create a new event.

    **Route:** ``/admin/events/create``

    **Methods:** ``GET, POST``
    """

    form = CreateEventForm(request.form)
    if form.validate_on_submit():
        try:
            EventsHelper.create_event(form, g.user)
        except EventumError.GCalAPI as e:
            flash(e.message, ERROR_FLASH)

        return redirect(url_for('.index'))
    if form.errors:
        for error in form.errors:
            for message in form.errors[error]:
                flash(message, ERROR_FLASH)

    upload_form = UploadImageForm()
    delete_form = DeleteEventForm()
    images = Image.objects()
    return render_template('eventum_events/create.html', form=form,
                           delete_form=delete_form, upload_form=upload_form,
                           images=images)


@events.route('/events/edit/<event_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit(event_id):
    """Edit an existing event.

    **Route:** ``/admin/events/edit/<event_id>``

    **Methods:** ``GET, POST``

    :param str event_id: The ID of the event to edit.
    """

    try:
        event = Event.objects().get(id=event_id)
    except (DoesNotExist, ValidationError):
        flash('Cannot find event with id "{}"'.format(event_id), ERROR_FLASH)
        return redirect(url_for('.index'))

    if request.method == "POST":
        form = EditEventForm(event, request.form)
    else:
        form = EventsHelper.create_form(event, request)

    if form.validate_on_submit():
        try:
            EventsHelper.update_event(event, form)
        except EventumError.GCalAPI as e:
            flash(e.message, ERROR_FLASH)

        return redirect(url_for('.index'))
    if form.errors:
        for error in form.errors:
            for message in form.errors[error]:
                flash(message, ERROR_FLASH)

    delete_form = DeleteEventForm()
    upload_form = UploadImageForm()
    images = Image.objects()

    return render_template('eventum_events/edit.html', form=form, event=event,
                           delete_form=delete_form, upload_form=upload_form,
                           images=images)


@events.route('/events/delete/<event_id>', methods=['POST'])
@requires_privilege('edit')
def delete(event_id):
    """Delete an existing event.

    **Route:** ``/admin/events/delete/<event_id>``

    **Methods:** ``POST``

    :param str event_id: The ID of the event to delete.
    """
    object_id = ObjectId(event_id)
    form = DeleteEventForm(request.form)
    if Event.objects(id=object_id).count() == 1:
        event = Event.objects().with_id(object_id)
        try:
            EventsHelper.delete_event(event, form)
        except EventumError.GCalAPI as e:
            flash(e.message, ERROR_FLASH)
    else:
        flash('Invalid event id', ERROR_FLASH)
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
                flash('Event published', MESSAGE_FLASH)
            else:
                event.date_published = None
                flash('Event unpublished', MESSAGE_FLASH)
            event.save()
        else:
            flash("The event had not been published.  No changes made.",
                  MESSAGE_FLASH)
    else:
        flash('Invalid event id', ERROR_FLASH)
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
