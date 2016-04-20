"""
.. module:: api
    :synopsis: All routes on the ``api`` Blueprint.

.. moduleauthor:: Jett Andersen <jettca1@gmail.com>
"""

from datetime import datetime, date, timedelta

from flask import Blueprint

from eventum.models import Event
from eventum.lib.json_response import json_success

api = Blueprint('api', __name__)


@api.route('/api/events/this_week', methods=['GET'])
def events_this_week():
    """
    Get a json object containing information about all the events for the
    current week (Sunday to Sunday).

    **Route:** ``/admin/api/events/this_week

    **Methods:** ``GET``
    """

    today = date.today()
    last_sunday = datetime.combine(
        today - timedelta(days=(today.isoweekday() % 7)),
        datetime.min.time())
    next_tuesday = last_sunday + timedelta(days=9)
    events = Event.objects(start_date__gte=last_sunday,
                           start_date__lt=next_tuesday).order_by('start_date')
    event_dicts = [event.to_jsonifiable() for event in events]

    return json_success(event_dicts)
