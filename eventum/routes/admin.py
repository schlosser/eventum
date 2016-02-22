"""
.. module:: admin
    :synopsis: All routes on the ``admin`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from eventum.lib.decorators import login_required
from flask import Blueprint, render_template, redirect, url_for
from datetime import date, timedelta, datetime
from eventum.models import Event, BlogPost

admin = Blueprint('admin', __name__)


@admin.route('/home', methods=['GET'])
@login_required
def index():
    """The homepage of Eventum. Shows the latest blog posts and events.

    **Route:** ``/admin/home``

    **Methods:** ``GET``
    """
    today = date.today()
    last_sunday = datetime.combine(
        today - timedelta(days=(today.isoweekday() % 7)),
        datetime.min.time())
    next_sunday = last_sunday + timedelta(days=7)

    this_week = (Event.objects(start_date__gt=last_sunday,
                               start_date__lt=next_sunday)
                 .order_by('start_date'))
    posts = BlogPost.objects().order_by('published', '-date_published')[:5]

    return render_template('eventum_home.html',
                           this_week=this_week,
                           recent_posts=posts)


@admin.route('/', methods=['GET'])
@login_required
def landing():
    """Redirects to the homepage.

    **Route:** ``/admin``

    **Methods:** ``GET``
    """
    return redirect(url_for('.index'))
