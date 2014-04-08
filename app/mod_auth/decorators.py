from flask import url_for, redirect, session, request, g
from app.mod_auth.controllers import lookup_current_user
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lookup_current_user()
        try:
            if g.user is None or 'openid' not in session:
                print "decoration"
                print session
                return redirect(url_for('auth.login', next=request.url))
            print g.user
        except AttributeError:
            return redirect(url_for('auth.login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function
