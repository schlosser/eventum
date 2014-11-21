"""
.. module:: decorators
    :synopsis: Decorators to be used on routes.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from eventum import app
from flask import url_for, redirect, session, request, g, abort
from functools import wraps
from mongoengine.queryset import DoesNotExist

SUPER_USER_GPLUS_ID = 'super'


def lookup_current_user():
    """Set the g.user variable to the User in the database that shares
    openid with the session, if one exists.

    Note that it gets called before all requests but not before decorators.
    """
    from eventum.models import User
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


def login_required(f):
    """A decorator requiring a user to be logged in.  Use this to decorate
    routes that require a user logged into Eventum to access.

    If there is no Google Plus ID in the session or user in the database,
    then redirect to login.  Else, run the decorated function.

    :param func f: The decorated function.
    :returns: The parameter function ``f``, but with checks for login.
    :rtype: func
    """
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
    """A decorator requiring a user to be logged in.  Use this to decorate
    routes that require a user logged into Eventum with a certain level of
    privilege to access.

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

        :param str privilege: The privilege that the logged in user should have
        It can be either ``"edit"``, ``"publish"``, or ``"admin"``.
        """
        self.privilege = privilege

    def __call__(self, f):
        """Call the decorator, on the decorated function, ``f``.

        :param func f: The decorated function.
        :returns: The parameter function ``f``, but with checks for login.
        :rtype: func
        """

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
