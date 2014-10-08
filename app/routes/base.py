from flask import g, session, render_template, request, redirect
from mongoengine.queryset import DoesNotExist
import requests

from app import app
from app.models import User

SUPER_USER_GPLUS_ID = 'super'

@app.errorhandler(404)
def not_found(error):
    old_site_url = 'http://adicu.github.com' + request.path
    try:
        response = requests.head(old_site_url, allow_redirects=True)
        if response.status_code == 200:
            return redirect(old_site_url)
    except requests.exceptions.ConnectionError:
        pass

    return render_template('error/404.html'), 404

@app.errorhandler(401)
def not_authorized(error):
    return render_template('error/401.html'), 401

@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('error/405.html', method=request.method), 405

@app.before_request
def lookup_current_user():
    """Set the g.user variable to the User in the database that shares
    openid with the session, if one exists.

    Note that it gets called before all requests, but not before decorators.
    """
    g.user = None
    if not app.config.get('GOOGLE_AUTH_ENABLED'):
        # bypass auth by mocking a super user
        session['gplus_id'] = SUPER_USER_GPLUS_ID
        try:
            g.user = User.objects.get(gplus_id=SUPER_USER_GPLUS_ID)
        except DoesNotExist:
            user = User(name='Super User',
                        gplus_id=SUPER_USER_GPLUS_ID,
                        user_type='admin',
                        email='email@email.com')
            user.save()

    if 'gplus_id' in session:
        gplus_id = session['gplus_id']
        try:
            g.user = User.objects().get(gplus_id=gplus_id)
        except DoesNotExist:
            pass  # Fail gracefully if the user is not in the database yet

@app.context_processor
def inject_user():
    return dict(current_user=g.user)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
