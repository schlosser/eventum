from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment
from client.config import setup

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
    app.config.from_object('client.config.config')
    app.config.update(config_overrides)

    # Initialize assets
    assets = Environment(app)
    setup.register_scss(app, assets)

    # Setup the database.
    db.init_app(app)

    # Add before and after requests, as well as context processors
    setup.setup_request_rules(app)

    setup.register_blueprints(app)
    setup.register_logging(app)
    setup.register_error_handlers(app)

    return app


def run():
    """Runs the app."""
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
