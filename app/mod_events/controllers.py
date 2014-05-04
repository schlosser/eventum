from flask import Blueprint, request, render_template, g, redirect, \
    url_for, session, flash, abort
from app.mod_events.models import Event
from app.mod_auth.models import User
from mongoengine.queryset import DoesNotExist
from app.mod_events.forms import CreateEventForm
from bson.objectid import ObjectId
from app.mod_auth.decorators import login_required, requires_privilege
from app.mod_events import utils
from datetime import datetime
mod_events = Blueprint('events', __name__)


@mod_events.before_request
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


@mod_events.route('/events')
@login_required
def events():
    """"""
    today_year, today_week, _ = datetime.now().isocalendar()
    today_index = today_year*52 + today_week
    events = {
        "this_week": [],
        "next_week": []
    }
    for event in [e for e in Event.objects() if e.start_date]:
        year, week, _ = event.start_date.isocalendar()
        index = year*52 + week
        print today_index,
        if index == today_index:
            events["this_week"].append(event)
        elif index == today_index + 1:
            events["next_week"].append(event)

    print events
    return render_template('events/events.html', events=events)


@mod_events.route('/events/create', methods=['GET', 'POST'])
@requires_privilege('edit')
def create_event():
    form = CreateEventForm(request.form)
    if form.validate_on_submit():
        event = utils.create_event(form, creator=g.user)
        event.save()
        return redirect(url_for('.events'))
    if form.errors:
        # print form.errors
        pass
    return render_template('events/create.html', form=form)

@mod_events.route('/events/edit/<event_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit_event(event_id):
    if Event.objects(id=event_id).count() != 1:
        abort(500) # Either invalid event ID or duplicate IDs.

    event = Event.objects().get(id=event_id)
    if request.method == 'POST':
        form = CreateEventForm(request.form)
        if form.validate_on_submit():
            event = utils.create_event(form, event=event)
            event.save()
            return redirect(url_for('.events'))
        flash("There was a validation error." + str(form.errors))
        return render_template('events/edit.html', form=form, event=event)
    form = utils.create_form(event, request)
    return render_template('events/edit.html', form=form, event=event)


@mod_events.route('/events/delete/<event_id>', methods=['POST'])
@requires_privilege('edit')
def delete_event(event_id):
    object_id = ObjectId(event_id)
    if Event.objects(id=object_id).count() == 1:
        event = Event.objects().with_id(object_id)
        event.delete()
    else:
        flash('Invalid event id')
        # print "Invalid event id"
        pass
    return redirect(url_for('.events'))


def set_published_status(event_id, status):
    object_id = ObjectId(event_id)
    if Event.objects(id=object_id).count() == 1:
        event = Event.objects().with_id(object_id)
        if status != event.published:
            event.published = status
            # TODO Actually publish/unpublish the event here
            if event.published:
                flash('Event published')
            else:
                flash('Event unpublished')
            event.save()
        else:
            flash("The event had not been published.  No changes made.")
    else:
        flash('Invalid event id')
        # print "Invalid event id"
        pass
    return redirect(url_for('.events'))


@mod_events.route('/events/publish/<event_id>', methods=['POST'])
@requires_privilege('publish')
def publish_event(event_id):
    return set_published_status(event_id, True)


@mod_events.route('/events/unpublish/<event_id>', methods=['POST'])
@requires_privilege('publish')
def unpublish_event(event_id):
    return set_published_status(event_id, False)


@mod_events.route('/events/view')
@requires_privilege('edit')
def view_events():
    return str(Event.objects())
