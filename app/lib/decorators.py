"""
.. module:: decorators
    :synopsis: Decorators to be used on routes.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app import app
from flask import url_for, redirect, session, request, g, abort
from functools import wraps

def login_required(f):
    """A decorator requiring a user to be logged in.

    If there is no Google Plus ID in the session or user in the database,
    then redirect to login.  Else, run the decorated function.

    :param func f: The decorated function.
    :returns: The parameter function ``f``, but with checks for login.
    :rtype: func
    """
    from app.routes.base import lookup_current_user
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """The decorated version of ``f`` (see :method:``login_required``).

        :param args: Arguments for ``f``.
        :params kwargs: Keyword arguments for ``f``.
        """

        lookup_current_user()
        try:
            if g.user is None or 'gplus_id' not in session:
                return redirect(url_for('auth.login', next=request.url))
        except AttributeError:
            return redirect(url_for('auth.login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function


class requires_privilege(object):
    """A decorator requiring a user to be logged in.

    If there is no Google Plus ID in the session or user in the database,
    then redirect to login.  Else, run the decorated function.

    Decorators like this that take parameters themselves must be
    implemented either as a three nested functions (ugly), or as a class
    (this implementation).  The ``__init__`` method creates the decorator,
    and is passed any arguments for how the decorator should behaive, and
    then the ``__call__`` method
    """

    def __init__(self, privilege):
        """Create a decorator to limit access to a decorated function to the
        secified privileges.

        :param str privilege: The privilege that the logged in user should have.
        It can be either ``"edit"``, ``"publish"``, or ``"admin"``.
        """
        self.privilege = privilege

    def __call__(self, f):
        """Call the decorator, on the decorated function, ``f``.

        :param func f: The decorated function.
        :returns: The parameter function ``f``, but with checks for login.
        :rtype: func
        """
        from app.routes.base import lookup_current_user

        @login_required
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """The decorated version of ``f`` (see :method:``__call__``).

            :param args: Arguments for ``f``.
            :params kwargs: Keyword arguments for ``f``.
            """
            lookup_current_user()
            try:
                if not g.user.can(self.privilege):
                    return abort(401)
            except AttributeError:
                return abort(401)

            return f(*args, **kwargs)
        return decorated_function


def development_only(f):
    """A decorator requiring a user to be logged in.

    If there is no Google Plus ID in the session or user in the database,
    then redirect to login.  Else, run the decorated function.

    :param func f: The decorated function.
    :returns: The parameter function ``f``, but with checks for login.
    :rtype: func
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """The decorated version of ``f`` (see :method:``development_only``).

        :param args: Arguments for ``f``.
        :params kwargs: Keyword arguments for ``f``.
        """

        if not app.config['DEBUG']:
            abort(401)
        return f(*args, **kwargs)

    return decorated_function
