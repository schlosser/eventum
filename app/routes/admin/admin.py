from app.lib.decorators import login_required
from flask import Blueprint, render_template, redirect, url_for
from datetime import date, timedelta, datetime
from app.models import Event, BlogPost

admin = Blueprint('admin', __name__)

@admin.route('/home')
@login_required
def index():
    today = date.today()
    last_sunday = datetime.combine(today - timedelta(days=(today.isoweekday() % 7)+7),
                                   datetime.min.time())
    next_sunday = last_sunday + timedelta(days=7)

    this_week = Event.objects(start_date__gt=last_sunday,
                              start_date__lt=next_sunday).order_by('start_date')
    posts = BlogPost.objects().order_by('published', '-date_published')[:5]

    return render_template("admin/home.html", this_week=this_week, recent_posts=posts)


@admin.route('/')
@login_required
def landing():
    return redirect(url_for('auth.login'))