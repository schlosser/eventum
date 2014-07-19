from app import app
from flask import url_for, redirect, session, request, g, abort
from functools import wraps

def login_required(f):
    """If there is no Google Plus ID in the session or user in the database,
    then redirect to login.  Else, run the decorated function.
    """
    from app.routes.base import lookup_current_user
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


class requires_privilege(object):

    def __init__(self, privilege):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.privilege = privilege

    def __call__(self, f):
        from app.routes.base import lookup_current_user

        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            lookup_current_user()
            try:
                if not g.user.can(self.privilege):
                    return abort(401)
            except AttributeError:
                return abort(401)

            return f(*args, **kwargs)
        return decorated_function


def development_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['DEBUG']:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function
