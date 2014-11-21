from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment
from eventum.config import setup

db = MongoEngine()
app = None
assets = None
gcal_client = None


def create_app(**config_overrides):
    """This is normal setup code for a Flask app, but we give the option
    to provide override configurations so that in testing, a different
    database can be used.
    """
    # we want to modify the global app, not a local copy
    global app
    global assets
    global gcal_client

    app = Flask(__name__)

    # Load config then apply overrides
    app.config.update(config_overrides)
    app.config.from_object('eventum.config.config')
    app.config.update(config_overrides)

    # Initialize assets
    assets = Environment(app)
    setup.register_scss(app, assets)

    # Setup the database.
    db.init_app(app)

    # Create gcal_client
    gcal_client = create_gcal_client(app)

    # Add before and after requests, as well as context processors
    setup.setup_request_rules(app)

    setup.register_delete_rules()
    setup.register_logging(app)
    setup.register_error_handlers(app)
    setup.register_blueprints(app)

    return app


def create_gcal_client(app):
    """Initialize the Google Calendar API Client, but only if the api
    credentials have been generated first.
    """
    if app.config.get('GOOGLE_AUTH_ENABLED'):
        try:
            from eventum.lib.google_calendar import GoogleCalendarAPIClient
            return GoogleCalendarAPIClient()
        except IOError:
            print """Failed to find the Google Calendar credentials file at
'{}', please create it by running:

    $ python manage.py --authorize
""".format(app.config['INSTALLED_APP_CREDENTIALS_PATH'])
            exit(1)


def run():
    """Runs the app."""
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
