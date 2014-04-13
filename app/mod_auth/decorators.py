from app import app
from flask import url_for, redirect, session, request, g, abort
from app.mod_auth.controllers import lookup_current_user
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lookup_current_user()
        try:
            if g.user is None or 'gplus_id' not in session:
                return redirect(url_for('auth.login', next=request.url))
            print g.user
        except AttributeError:
            return redirect(url_for('auth.login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function

def development_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print app.debug
        if not app.debug:
            print "aborting"
            abort(401)
        return f(*args, **kwargs)
    return decorated_function
