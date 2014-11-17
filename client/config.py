from os import environ, path, pardir
from sys import exit
import json

# configurations that are specific to ADI's Eventum flavor

# Default Event Image
DEFAULT_EVENT_IMAGE = 'img/events/default_event.png'

# Resources
RESOURCES_PATH = 'client/data/resources.json'

# Labs FAQ
FAQ_PATH = 'client/data/labs_faq.json'

# Jobfair Companies
COMPANIES_PATH = 'client/data/companies.json'


try:
    # basic flask settings
    HOST = environ.get('CLIENT_HOST', '0.0.0.0')
    PORT = int(environ.get('CLIENT_PORT', 5001))
    SECRET_KEY = environ['CLIENT_SECRET_KEY']
    DEBUG = True if environ['CLIENT_DEBUG'] == 'TRUE' else False

    # Cross-site request forgery settings
    CSRF_ENABLED = True if environ['CLIENT_CSRF_ENABLED'] == 'TRUE' else False
    CSRF_SESSION_KEY = environ['CLIENT_CSRF_SESSION_KEY']

    # Mongo configs
    MONGODB_SETTINGS = {'DB': environ.get('MONGO_DATABASE', 'eventum')}

    # Logging settings
    LOG_FILE_MAX_SIZE = environ.get("CLIENT_LOG_FILE_MAX_SIZE")
    APP_LOG_NAME = environ.get("CLIENT_APP_LOG_NAME")
    WERKZEUG_LOG_NAME = environ.get("CLIENT_WERKZEUG_LOG_NAME")

except KeyError:
    # Throw an error if a setting is missing.
    print ("Some of your settings aren't in the environment."
    "You probably need to run:\n\n\tsource config/<your settings file>")
    exit(1)