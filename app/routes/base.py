"""
.. module:: base
    :synopsis: All routes on the ``base`` Blueprint, as well as error handlers,
        before and after request handlers, and context processors.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

import sys
from flask import g, session, render_template, request, redirect, Blueprint
from mongoengine.queryset import DoesNotExist
import requests

from app import app
from app.models import User

SUPER_USER_GPLUS_ID = 'super'

base = Blueprint('base', __name__)

@app.errorhandler(Exception)
def exceptionHandler(error):
    """Handle uncaught exceptions."""
    app.logger.error("Uncaught Exception", exc_info=sys.exc_info())
    app.handle_exception(error) # default error handler

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return render_template('error/400.html'), 400

@app.errorhandler(401)
def not_authorized(error):
    """Handle 401 errors."""
    return render_template('error/401.html'), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors."""
    return render_template('error/403.html'), 403

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    old_site_url = 'http://adicu.github.com' + request.path
    try:
        response = requests.head(old_site_url, allow_redirects=True)
        if response.status_code == 200:
            return redirect(old_site_url)
    except requests.exceptions.ConnectionError:
        pass

    return render_template('error/404.html'), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return render_template('error/405.html', method=request.method), 405

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('error/500.html'), 500

@base.before_request
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
    """Injects a variable named ``current_user`` into all of the Jinja
    templates, so that it can be used at will.
    """
    if hasattr(g, 'user'):
        return dict(current_user=g.user)
    return dict(current_user=None)

@base.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
