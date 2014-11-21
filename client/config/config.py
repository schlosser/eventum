from os import environ
from sys import exit

# Configurations that are specific to ADI's Eventum flavor
try:
    # basic flask settings
    HOST = environ['CLIENT_HOST']
    PORT = int(environ['CLIENT_PORT'])
    SERVER_NAME = environ['CLIENT_SERVER_NAME']
    SECRET_KEY = environ['CLIENT_SECRET_KEY']
    DEBUG = environ['CLIENT_DEBUG'] == 'TRUE'

    # Cross-site request forgery settings
    CSRF_ENABLED = environ['CLIENT_CSRF_ENABLED'] == 'TRUE'
    CSRF_SESSION_KEY = environ['CLIENT_CSRF_SESSION_KEY']

    # Mongo configs
    MONGODB_SETTINGS = {'DB': environ['CLIENT_MONGO_DATABASE']}

    # Logging settings
    LOG_FORMAT = environ['CLIENT_LOG_FORMAT']
    LOG_FILE_MAX_SIZE = environ["CLIENT_LOG_FILE_MAX_SIZE"]
    APP_LOG_NAME = environ["CLIENT_APP_LOG_NAME"]
    WERKZEUG_LOG_NAME = environ["CLIENT_WERKZEUG_LOG_NAME"]

except KeyError as e:
    # Throw an error if a setting is missing
    print ("""
Some of your settings aren't in the environment. Couldn't find the environment
variable {}. You probably need to run:

    source config/<your settings file>""".format(e.args[0]))
    exit(1)


RESOURCES_PATH = 'client/data/resources.json'
FAQ_PATH = 'client/data/labs_faq.json'
COMPANIES_PATH = 'client/data/companies.json'
SCSS_JSON_PATH = 'client/config/scss.json'
