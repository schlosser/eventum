from sys import argv, exit
from oauth2client.file import Storage
from config import flask_config

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run


def authorize_google_calendar():
    FLOW = OAuth2WebServerFlow(
        client_id=flask_config.CLIENT_ID,
        client_secret=flask_config.CLIENT_SECRET,
        scope='https://www.googleapis.com/auth/calendar',
        user_agent='EVENTUM/0.1')

    # Save the credentials file here for use by the app
    storage = Storage(flask_config.CREDENTIALS_PATH)
    run(FLOW, storage)

def print_usage():
    print "Usage:"
    print "%s --authorize (-a) Authorize the Google Calendar API Client"

if __name__ == '__main__':
    if len(argv) >=2 and len(argv) <= 3:
        if '--authorize' in argv or '-a' in argv:
            authorize_google_calendar()
    else:
        print_usage()
        exit(1)
