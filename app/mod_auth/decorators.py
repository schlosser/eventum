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
        except AttributeError:
            return redirect(url_for('auth.login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function


class requires_privelage(object):

    def __init__(self, privelage):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.privelage = privelage

    def __call__(self, f):
        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            lookup_current_user()
            try:
                if not g.user.can(self.privelage):
                    return abort(401)
            except AttributeError:
                return abort(401)

            return f(*args, **kwargs)
        return decorated_function


def development_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['DEBUG']:
            print "aborting"
            abort(401)
        return f(*args, **kwargs)
    return decorated_function
