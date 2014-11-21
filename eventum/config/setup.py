import logging

from flask import g
from common.error_handlers import error_handlers
from common.setup import register_scss as common_register_scss

register_scss = common_register_scss


def setup_request_rules(app):

    @app.context_processor
    def modify_contex():
        """Injects a variable named ``current_user`` into all of the Jinja
        templates, so that it can be used at will.
        """
        from common.interface import client_url_for
        context = {
            'client_url_for': client_url_for
        }
        if hasattr(g, 'user'):
            context['current_user'] = g.user
        return context

    @app.after_request
    def add_header(response):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response


def register_error_handlers(app):
    """Register the error handlers for HTTP errors, as well as exception
    handling.
    """
    for _, (error_type, error_handler) in error_handlers.iteritems():
        app.error_handler_spec[None][error_type] = error_handler


def register_logging(app):
    """Registers all the loggers for the app.  Redirects error output to files
    as specified in config.py
    """
    maxBytes = int(app.config["LOG_FILE_MAX_SIZE"]) * 1024 * 1024   # MB to B
    Handler = logging.handlers.RotatingFileHandler
    fStr = app.config['LOG_FORMAT']

    accessHandler = Handler(app.config["WERKZEUG_LOG_NAME"], maxBytes=maxBytes)
    accessHandler.setLevel(logging.INFO)
    logging.getLogger("werkzeug").addHandler(accessHandler)

    appHandler = Handler(app.config["APP_LOG_NAME"], maxBytes=maxBytes)
    formatter = logging.Formatter(fStr)
    appHandler.setLevel(logging.INFO)
    appHandler.setFormatter(formatter)

    app.logger.addHandler(appHandler)


def register_blueprints(app):
    """Registers all the Blueprints (modules) in a function, to avoid
    circular dependancies.

    Be careful rearranging the order of the app.register_blueprint()
    calls, as it can also result in circular dependancies.
    """
    from eventum.routes import (admin, auth, events, media, posts,
                                users, whitelist)
    admin_blueprints = [admin, auth, events, media, posts, users, whitelist]

    for bp in admin_blueprints:
        app.register_blueprint(bp)


def register_delete_rules():
    """Registers rules for how Mongoengine handles the deletion of objects
    that are being referenced by other objects.

    See the documentation for :func:`mongoengine.model.register_delete_rule`
    for more information.

    All delete rules for User fields must by DENY, because User objects should
    never be deleted.  Lists of reference fields should PULL, to remove deleted
    objects from the list, and all others should NULLIFY
    """
    from eventum.models import Event, EventSeries, User, Post, BlogPost, Image
    from mongoengine import NULLIFY, PULL, DENY

    Event.register_delete_rule(EventSeries, 'events', PULL)
    Image.register_delete_rule(BlogPost, 'images', PULL)
    Image.register_delete_rule(User, 'image', NULLIFY)
    Image.register_delete_rule(BlogPost, 'featured_image', NULLIFY)
    Image.register_delete_rule(Event, 'image', NULLIFY)
    EventSeries.register_delete_rule(Event, 'parent_series', NULLIFY)
    User.register_delete_rule(Event, 'creator', DENY)
    User.register_delete_rule(Image, 'creator', DENY)
    User.register_delete_rule(Post, 'author', DENY)
    User.register_delete_rule(Post, 'posted_by', DENY)
