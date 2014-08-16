from sys import argv, exit
from oauth2client.file import Storage
from config import flask_config

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from script import backfill_blog, import_images

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
    print "%s --authorize (-a)     Authorize the Google Calendar API Client" % argv[0]
    print "%s --backfill-blog (-b) Backfill blog posts from data/jekyll-posts" % argv[0]
    print "%s --import-images (-i) Import images from data/jekyll-images" % argv[0]

if __name__ == '__main__':
    if '--authorize' in argv or '-a' in argv:
        authorize_google_calendar()
    elif '--backfill-blog' in argv or '-b' in argv:
        backfill_blog.backfill_from_jekyll('data/jekyll-posts')
    elif '--import-images' in argv or '-i' in argv:
        import_images.import_from_directory('data/jekyll-images')
    else:
        print_usage()
        exit(1)
