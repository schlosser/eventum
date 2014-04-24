from flask import Blueprint, request, render_template, g, redirect, \
    url_for, session, flash
from app.mod_events.models import Event
from app.mod_auth.models import User
from mongoengine.queryset import DoesNotExist
from app.mod_events.forms import CreateEventForm
from datetime import datetime
from bson.objectid import ObjectId
from app.mod_auth.decorators import login_required, requires_privilege

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
    events = Event.objects()
    return render_template('events/events.html', the_events=events)


@mod_events.route('/events/create', methods=['GET', 'POST'])
@requires_privilege('edit')
def create_event():
    form = CreateEventForm(request.form)
    if form.validate_on_submit():
        event = Event(title=form.title.data,
                      creator=g.user,
                      published=False)
        if form.has_date_fields():
            event.start_datetime = datetime.combine(form.start_date.data,
                                                    form.start_time.data)
            event.end_datetime = datetime.combine(form.end_date.data,
                                                  form.end_time.data)
        if form.location.data:
            event.location = form.location.data
        if form.short_description.data:
            event.descriptions["short"] = form.short_description.data
        if form.long_description.data:
            event.descriptions["long"] = form.long_description.data
        event.save()
        return redirect(url_for('.events'))
    if form.errors:
        # print form.errors
        pass
    return render_template('events/create_event.html', form=form)


@mod_events.route('/events/delete/<_id>', methods=['POST'])
@requires_privilege('edit')
def delete_event(_id):
    object_id = ObjectId(_id)
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
            flash('Event published')
            # TODO Actually unpublish the event here
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
