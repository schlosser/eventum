from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment, Bundle
import json

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
    app.config.from_object('config.flask_config')
    app.config.update(config_overrides)

    # Initialize assets
    assets = Environment(app)
    register_scss()

    # Setup the database.
    db.init_app(app)

    # Initialize the Google Calendar API Client, but only if the api
    # credentials have been generated first.
    try:
        from app.lib.google_calendar import GoogleCalendarAPIClient
        gcal_client = GoogleCalendarAPIClient()
    except IOError:
        print ('Failed to find the Google Calendar credentials file at \'%s\', '
               'please create it by running:\n\n'
               '    $ python manage.py --authorize\n' % app.config['CREDENTIALS_PATH'])
        exit(1)


    register_blueprints()


def register_blueprints():
    """Registers all the Blueprints (modules) in a function, to avoid
    circular dependancies.

    Be careful rearranging the order of the app.register_blueprint()
    calls, as it can also result in circular dependancies.
    """
    from app.auth.controllers import auth as auth_module
    from app.base.controllers import base as base_module
    from app.learn.controllers import learn as learn_module
    from app.events.controllers import events as events_module
    from app.blog.controllers import blog as blog_module
    from app.media.controllers import media as media_module
    from app.networking.controllers import networking as \
        networking_module

    admin_blueprints = [auth_module, base_module, learn_module, events_module, blog_module, media_module, networking_module,


def register_scss():
    """"""
    assets.url = app.static_url_path
    defaults = {
        'filters':'scss',
        'depends':['scss/_colors.scss', 'scss/app.scss']
    }

    with open('config/scss.json') as f:
        bundle_instructions = json.loads(f.read())
        for bundle_name, instructions in bundle_instructions.iteritems():
            bundle = Bundle(*instructions["inputs"],
                            output=instructions["output"],
                            **defaults)
            assets.register(bundle_name, bundle)


def run():
	app.run(host='0.0.0.0', port=5000)
