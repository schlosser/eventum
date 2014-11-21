import json
import logging
from flask.ext.assets import Bundle
from client.config.error_handlers import error_handlers
from flask import g


def setup_request_rules(app):

    @app.context_processor
    def modify_contex():
        """Injects a variable named ``current_user`` into all of the Jinja
        templates, so that it can be used at will.
        """
        from common.interface import eventum_url_for
        context = {
            'eventum_url_for': eventum_url_for
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
    from client.routes import blog, home
    blueprints = [blog, home]

    for bp in blueprints:
        app.register_blueprint(bp)


def register_scss(app, assets):
    """Registers the Flask-Assets rules for scss compilation.  This reads from
    ``eventum/config/scss.json`` to make these rules.
    """
    assets.url = app.static_url_path
    with open(app.config['SCSS_JSON_PATH']) as f:
        bundle_instructions = json.loads(f.read())
        for _, bundle_set in bundle_instructions.iteritems():
            output_folder = bundle_set['output_folder']
            depends = bundle_set['depends']
            for bundle_name, instructions in bundle_set['rules'].iteritems():
                bundle = Bundle(*instructions['inputs'],
                                output=output_folder + instructions['output'],
                                depends=depends,
                                filters='scss')
                assets.register(bundle_name, bundle)
