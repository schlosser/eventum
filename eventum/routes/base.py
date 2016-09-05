"""
.. module:: base
    :synopsis: All routes on the ``base`` Blueprint, as well as error handlers,
        before and after request handlers, and context processors.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import sys
from flask import (g, session, render_template, request, redirect, flash,
                   url_for, current_app)
from mongoengine.queryset import DoesNotExist
from eventum.models import User

SUPER_USER_GPLUS_ID = 'super'
ERROR_FLASH = 'error'
MESSAGE_FLASH = 'message'


def lookup_current_user():
    """Set the g.user variable to the User in the database that shares
    openid with the session, if one exists.

    Note that it gets called before all requests, but not before decorators
    """
    g.user = None
    if not current_app.config.get('EVENTUM_GOOGLE_AUTH_ENABLED'):
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


def register_error_handlers(blueprint):

    @blueprint.errorhandler(Exception)
    def exception_handler(error):
        """Handle uncaught exceptions."""
        current_app.logger.error("Uncaught Exception", exc_info=sys.exc_info())
        if (not current_app.config['DEBUG'] and
                request.path.startswith('/admin')):
            flash('An uncaught error occured: {}'.format(error.strerror),
                  ERROR_FLASH)
            return redirect(url_for('admin.index'))
        current_app.handle_exception(error)  # default error handler

    @blueprint.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors."""
        return render_template('eventum_error/400.html'), 400

    @blueprint.errorhandler(401)
    def not_authorized(error):
        """Handle 401 errors."""
        return render_template('eventum_error/401.html'), 401

    @blueprint.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors."""
        return render_template('eventum_error/403.html'), 403

    @blueprint.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template('eventum_error/404.html'), 404

    @blueprint.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        response = render_template("eventum_error/405.html",
                                   method=request.method)
        return response, 405


def configure_routing(app):

    @app.before_request
    def _lookup_current_user():
        """We need to be able to import :func:`lookup_current_user`, so
        it can't be defined within :func:`register_error_handlers`, so
        this method serves as an way to do both.
        """
        lookup_current_user()

    @app.context_processor
    def inject_helpers():
        """Injects a dictionary of helper variables and functions into
        Jinja templates.
        """
        helpers = {
            'current_user': None
        }

        if hasattr(g, 'user'):
            helpers['current_user'] = g.user

        return helpers

    @app.after_request
    def add_header(response):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response
