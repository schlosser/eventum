from os import environ, path, pardir
from sys import exit
import json

try:
    # basic flask settings
    HOST = environ.get('HOST', '0.0.0.0')
    PORT = int(environ.get('PORT', 5000))
    SECRET_KEY = environ['SECRET_KEY']
    DEBUG = True if environ['DEBUG'] == 'TRUE' else False

    # credentials that allow the app to modify calendars without using a
    # without a user's login
    INSTALLED_APP_SECRET_PATH = environ.get('INSTALLED_APP_CLIENT_SECRET_PATH',
                                               'client_secrets.json')
    # where the installed credentials are stored
    INSTALLED_APP_CREDENTIALS_PATH = environ.get('INSTALLED_APP_CREDENTIALS_PATH',
                                   'config/credentials.json')

    # Google Auth
    # This is used for the webapp that allows Google+ login
    GOOGLE_AUTH_ENABLED = True if environ['GOOGLE_AUTH_ENABLED'] == 'TRUE' \
                            else False
    CLIENT_SECRETS_PATH = environ.get('GOOGLE_AUTH_SECRETS',
                                      'config/client_secrets.json')

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

        except IOError:
            print ("The Google client_secrets file was not found at"
                   "'{}', check that it exists.".format(CLIENT_SECRETS_PATH))
            exit(1)

    # Cross-site request forgery settings
    CSRF_ENABLED = True if environ['CSRF_ENABLED'] == 'TRUE' else False
    CSRF_SESSION_KEY = environ['CSRF_SESSION_KEY']

    # Google Calendar credentials
    PRIVATE_CALENDAR_ID = environ['PRIVATE_CALENDAR_ID']
    PUBLIC_CALENDAR_ID =  environ['PUBLIC_CALENDAR_ID']

    # Mongo configs
    MONGODB_SETTINGS = {'DB': environ.get('MONGO_DATABASE', 'eventum')}


except KeyError:
    """ Throw an error if a setting is missing """
    print ("Some of your settings aren't in the environment."
    "You probably need to run:\n\n\tsource config/<your settings file>")
    exit(1)


############################################################################
#  Constants in version control
############################################################################

# Base directory
BASEDIR = path.abspath(path.join(path.dirname(__file__), pardir))

RELATIVE_UPLOAD_FOLDER = 'app/static/img/uploaded/'
UPLOAD_FOLDER = path.join(BASEDIR, RELATIVE_UPLOAD_FOLDER)
RELATIVE_DELETE_FOLDER = 'app/static/img/uploaded/deleted/'
DELETE_FOLDER = path.join(BASEDIR, RELATIVE_DELETE_FOLDER)

# The file extensions that may be uploaded
ALLOWED_UPLOAD_EXTENSIONS = set(['.txt',
    '.pdf',
    '.png',
    '.jpg',
    '.jpeg',
    '.gif'
])
