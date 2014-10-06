import json
from sys import exit

# Flask Debug mode
DEBUG = True

# Form CSRF protection
CSRF_ENABLED = True
CSRF_SESSION_KEY = '[[ REDACTED ]]'

# Whether or not to enable Google Auth or not.
AUTH = True
# Google Auth config
CLIENT_SECRETS_PATH = 'config/client_secrets.json'
CREDENTIALS_PATH = 'config/credentials.json'

# Setup Google Auth
if AUTH:
    try:
        with open(CLIENT_SECRETS_PATH, 'r') as f:
            _secrets_data = json.loads(f.read())['web']
            CLIENT_ID = _secrets_data['client_id']
            CLIENT_SECRET = _secrets_data['client_secret']
    except IOError:
        print "The Google client_secrets file was not found at '%s', check that it exists." % CLIENT_SECRETS_PATH
        exit(1)

# Google Calendar configs
PRIVATE_CALENDAR_ID = '[[ REDACTED ]]'
PUBLIC_CALENDAR_ID = '[[ REDACTED ]]'

# For Cookies
SECRET_KEY = '[[ REDACTED ]]'

# Mongo configs
MONGODB_SETTINGS = {'DB': 'eventum'}

# Base directory
import os
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Folders
RELATIVE_UPLOAD_FOLDER = 'app/static/img/uploaded/'
UPLOAD_FOLDER = os.path.join(BASEDIR, RELATIVE_UPLOAD_FOLDER)
RELATIVE_DELETE_FOLDER = 'app/static/img/uploaded/deleted/'
DELETE_FOLDER = os.path.join(BASEDIR, RELATIVE_DELETE_FOLDER)

# The file extensions that may be uploaded
ALLOWED_EXTENSIONS = set(['.txt',
 '.pdf',
 '.png',
 '.jpg',
 '.jpeg',
 '.gif'])

# Default Event Image
DEFAULT_EVENT_IMAGE = 'img/events/default_event.png'

# Resources
RESOURCES_PATH = 'data/resources.json'

# Labs FAQ
FAQ_PATH = 'data/labs_faq.json'

# Jobfair Companies
COMPANIES_PATH = 'data/companies.json'
