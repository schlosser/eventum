from os import environ, path, pardir
from sys import exit
import json

try:
    # basic flask settings
    HOST = environ['EVENTUM_HOST']
    PORT = int(environ['EVENTUM_PORT'])
    SERVER_NAME = environ['EVENTUM_SERVER_NAME']
    SECRET_KEY = environ['EVENTUM_SECRET_KEY']
    DEBUG = environ['EVENTUM_DEBUG'] == 'TRUE'

    # Cross-site request forgery settings
    CSRF_ENABLED = environ['EVENTUM_CSRF_ENABLED'] == 'TRUE'
    CSRF_SESSION_KEY = environ['EVENTUM_CSRF_SESSION_KEY']

    # Mongo configs
    MONGODB_SETTINGS = {'DB': environ['EVENTUM_MONGO_DATABASE']}

    # Logging settings
    LOG_FORMAT = environ['EVENTUM_LOG_FORMAT']
    LOG_FILE_MAX_SIZE = environ['EVENTUM_LOG_FILE_MAX_SIZE']
    APP_LOG_NAME = environ['EVENTUM_APP_LOG_NAME']
    WERKZEUG_LOG_NAME = environ['EVENTUM_WERKZEUG_LOG_NAME']

    # Google Calendar credentials
    PRIVATE_CALENDAR_ID = environ['EVENTUM_PRIVATE_CALENDAR_ID']
    PUBLIC_CALENDAR_ID = environ['EVENTUM_PUBLIC_CALENDAR_ID']

    # credentials that allow the app to modify calendars without using a
    # without a user's login
    INSTALLED_APP_SECRET_PATH = \
        environ['EVENTUM_INSTALLED_APP_CLIENT_SECRET_PATH']
    # where the installed credentials are stored
    INSTALLED_APP_CREDENTIALS_PATH = \
        environ['EVENTUM_INSTALLED_APP_CREDENTIALS_PATH']

    # Google Auth
    # This is used for the webapp that allows Google+ login
    GOOGLE_AUTH_ENABLED = environ['EVENTUM_GOOGLE_AUTH_ENABLED'] == 'TRUE'

    CLIENT_SECRETS_PATH = environ['EVENTUM_GOOGLE_AUTH_SECRETS']

    # Setup Google Auth
    if GOOGLE_AUTH_ENABLED:
        try:
            with open(CLIENT_SECRETS_PATH, 'r') as f:
                _secrets_data = json.loads(f.read())['web']
                GOOGLE_CLIENT_ID = _secrets_data['client_id']

                if not _secrets_data.get('client_secret', None):
                    print ('Google Auth config file, %s,'
                           ' missing client secret', CLIENT_SECRETS_PATH)
                    exit(1)

        except (IOError, KeyError):
            print ("""
The Google client_secrets file was not found at \'{}\' or was malformed. Please
check that it exists and is formatted properly.""".format(CLIENT_SECRETS_PATH))
            exit(1)

except KeyError as e:
    # Throw an error if a setting is missing
    print ("""
Some of your settings aren't in the environment. Couldn't find the environment
variable {}. You probably need to run:

    source config/<your settings file>""".format(e.args[0]))
    exit(1)


############################################################################
#  Constants in version control
############################################################################

# Base directory
BASEDIR = path.abspath(path.join(path.dirname(__file__), pardir))

DEFAULT_EVENT_IMAGE = 'img/events/default_event.png'
RELATIVE_UPLOAD_FOLDER = 'eventum/static/img/uploaded/'
UPLOAD_FOLDER = path.join(BASEDIR, RELATIVE_UPLOAD_FOLDER)
RELATIVE_DELETE_FOLDER = 'eventum/static/img/uploaded/deleted/'
DELETE_FOLDER = path.join(BASEDIR, RELATIVE_DELETE_FOLDER)
SCSS_JSON_PATH = 'eventum/config/scss.json'

# The file extensions that may be uploaded
ALLOWED_UPLOAD_EXTENSIONS = set(['.txt',
                                 '.pdf',
                                 '.png',
                                 '.jpg',
                                 '.jpeg',
                                 '.gif'])
