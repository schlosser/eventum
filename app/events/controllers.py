from flask import Blueprint, request, render_template, g, redirect, \
    url_for, session, flash, abort
from app.events.models import Event
from app.auth.models import User
from mongoengine.queryset import DoesNotExist
from app.events.forms import CreateEventForm, DeleteEventForm
from bson.objectid import ObjectId
from app.auth.decorators import login_required, requires_privilege
from app.events import utils
from datetime import datetime
events = Blueprint('events', __name__)


@events.before_request
def lookup_current_user():
    """Set the g.user variable to the User in the database that shares
    openid with the session, if one exists.

    Note that it gets called before all requests, but not before decorators.
    """
    g.user = None
    if 'gplus_id' in session:
        gplus_id = session['gplus_id']
        try:
            g.user = User.objects().get(gplus_id=gplus_id)
        except DoesNotExist:
            pass  # Fail gracefully if the user is not in the database yet


@events.route('/events')
@login_required
def index():
    """"""
    offset = int(request.args.get('week')) if request.args.get('week') else 0
    today_year, today_week, _ = datetime.now().isocalendar()
    today_index = today_year*52 + today_week + 2*offset
    events = {
        "this_week": [],
        "next_week": []
    }
    for event in [e for e in Event.objects() if e.start_date]:
        year, week, _ = event.start_date.isocalendar()
        index = year*52 + week
        if index == today_index:
            events["this_week"].append(event)
        elif index == today_index + 1:
            events["next_week"].append(event)

    return render_template('events/events.html', events=events)


@events.route('/events/create', methods=['GET', 'POST'])
@requires_privilege('edit')
def create_event():
    """"""
    form = CreateEventForm(request.form)
    delete_form = DeleteEventForm()
    if form.validate_on_submit():
        utils.create_event(form, creator=g.user)
        return redirect(url_for('.index'))
    if form.errors:
        flash("There was a validation error." + str(form.errors))
        pass
    return render_template('events/create.html', form=form, user=g.user,
                           delete_form=delete_form)

@events.route('/events/edit/<event_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit_event(event_id):
    """"""
    if Event.objects(id=event_id).count() != 1:
        abort(500) # Either invalid event ID or duplicate IDs.

    event = Event.objects().get(id=event_id)
    delete_form = DeleteEventForm()

    form = CreateEventForm(request.form) if request.method == 'POST' else \
        utils.create_form(event, request)

    if form.validate_on_submit():
        utils.update_event(event, form, update_all=form.update_all.data,
                           update_following=form.update_following.data)
        return redirect(url_for('.index'))
    if form.errors:
        flash("There was a validation error." + str(form.errors))

    return render_template('events/edit.html', form=form, event=event,
                           user=g.user, delete_form=delete_form)


@events.route('/events/delete/<event_id>', methods=['POST'])
@requires_privilege('edit')
def delete_event(event_id):
    """"""
    object_id = ObjectId(event_id)
    form = DeleteEventForm(request.form)
    if Event.objects(id=object_id).count() == 1:
        event = Event.objects().with_id(object_id)
        if event.is_recurring:
            series = event.parent_series
            # Delete the desired subset of events from the series
            if form.delete_following.data:
                series.delete_following(event)
            elif form.delete_all.data:
                print "here"
                series.delete_all()
            else:
                series.delete_one(event)
        else:
            # The event is not recurring, so just delete it
            event.delete()
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
        # print "Invalid event id"
        pass
    return redirect(url_for('.index'))


@events.route('/events/publish/<event_id>', methods=['POST'])
@requires_privilege('publish')
def publish_event(event_id):
    """"""
    return set_published_status(event_id, True)


@events.route('/events/unpublish/<event_id>', methods=['POST'])
@requires_privilege('publish')
def unpublish_event(event_id):
    """"""
    return set_published_status(event_id, False)


@events.route('/events/view')
@requires_privilege('edit')
def view_events():
    return str(Event.objects())

@events.route('/mom')
def mom():
    for e in Event.objects():
        e.delete()
    return "hi"
