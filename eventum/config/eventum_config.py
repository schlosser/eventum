from os import path, pardir
import eventum

# Default Values
CSRF_ENABLED = True
MONGODB_SETTINGS = {
    'DB': 'eventum'
}
EVENTUM_DEFAULT_PROFILE_PICTURE = 'http://www.foggybottommilkrun.com/assets/records/4-mile%20record%20men-ad7803638fa6b3b80c7a755ce575ff98.jpg'
EVENTUM_DEFAULT_EVENT_IMAGE = 'http://www.foggybottommilkrun.com/assets/records/4-mile%20record%20men-ad7803638fa6b3b80c7a755ce575ff98.jpg'
EVENTUM_GOOGLE_AUTH_ENABLED = True
EVENTUM_APP_LOG_NAME = 'app.log'
EVENTUM_WERKZEUG_LOG_NAME = 'werkzeug.log'
EVENTUM_LOG_FILE_MAX_SIZE = 256
EVENTUM_URL_PREFIX = '/admin'
EVENTUM_ALLOWED_UPLOAD_EXTENSIONS = set(['.png', '.jpg', '.jpeg', '.gif'])

EVENTUM_BASEDIR = eventum.__path__[0]

# Static folder
EVENTUM_STATIC_FOLDER = path.join(EVENTUM_BASEDIR,
                                  'static/')
# SCSS folder
EVENTUM_SCSS_FOLDER = path.join(EVENTUM_STATIC_FOLDER,
                                'eventum_scss/')
# Template folder
EVENTUM_TEMPLATE_FOLDER = path.join(EVENTUM_BASEDIR,
                                    'templates/')

######################
# Must be overridden #
######################

EVENTUM_INSTALLED_APP_CLIENT_SECRET_PATH = None
EVENTUM_INSTALLED_APP_CREDENTIALS_PATH = None
EVENTUM_CLIENT_SECRETS_PATH = None
EVENTUM_PRIVATE_CALENDAR_ID = None
EVENTUM_PUBLIC_CALENDAR_ID = None
EVENTUM_UPLOAD_FOLDER = None
EVENTUM_DELETE_FOLDER = None

# Will be set elsewhere, do not set directly
EVENTUM_GOOGLE_CLIENT_ID = None
