from flask import g, session, render_template, request
from mongoengine.queryset import DoesNotExist

from app import app
from app.models import User

@app.errorhandler(404)
def not_found(error):
    return render_template('admin/error/404.html'), 404

@app.errorhandler(401)
def not_authorized(error):
    return render_template('admin/error/401.html'), 401

@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('admin/error/405.html', method=request.method), 405

@app.before_request
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

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response