from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment, Bundle
import json

from config import adi_config

db = MongoEngine()
app = None
adi = dict()
assets = None
gcal_client = None

def create_app(**config_overrides):
    """This is normal setup code for a Flask app, but we give the option
    to provide override configurations so that in testing, a different
    database can be used.
    """
    # we want to modify the global app, not a local copy
    global app
    global adi
    global assets
    global gcal_client
    app = Flask(__name__)

    # Load config then apply overrides
    app.config.update(config_overrides)
    app.config.from_object('config.flask_config')
    app.config.update(config_overrides)

    # load ADI specific configurations (ignore built-in methods)
    for attr in (x for x in dir(adi_config) if x[:2] != "__"):
        adi[attr] = getattr(adi_config, attr)

    # Initialize assets
    assets = Environment(app)
    register_scss()

    # Setup the database.
    db.init_app(app)

    # Initialize the Google Calendar API Client, but only if the api
    # credentials have been generated first.
    if app.config.get('GOOGLE_AUTH_ENABLED'):
        try:
            from app.lib.google_calendar import GoogleCalendarAPIClient
            gcal_client = GoogleCalendarAPIClient()
        except IOError:
            print ('Failed to find the Google Calendar credentials file at \'%s\', '
                   'please create it by running:\n\n'
                   '    $ python manage.py --authorize\n'
                   % app.config['INSTALLED_APP_CREDENTIALS_PATH'])
            exit(1)

    register_blueprints()
    register_delete_rules()

    return app

def register_blueprints():
    """Registers all the Blueprints (modules) in a function, to avoid
    circular dependancies.

    Be careful rearranging the order of the app.register_blueprint()
    calls, as it can also result in circular dependancies.
    """
    from app.routes.admin import (admin, auth, events, resources, media, posts,
                                  users, whitelist)
    admin_blueprints = [admin, auth, events, resources, media, posts, users,
                        whitelist]

    for bp in admin_blueprints:
        app.register_blueprint(bp, url_prefix="/admin")

    from app.routes import base; assert base # Not a blueprint, but should be imported
    from app.routes import blog, client
    blueprints = [blog, client]

    for bp in blueprints:
        app.register_blueprint(bp)

def register_delete_rules():
    """

    All delete rules for User fields must by DENY, because User objects should
    never be deleted.  Lists of reference fields should PULL, to remove deleted
    objects from the list, and all others should NULLIFY
    """
    from app.models import Event, EventSeries, User, Post, BlogPost, Image
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

def register_scss():
    """"""
    assets.url = app.static_url_path
    with open('config/scss.json') as f:
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

def run():
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
