import gflags
from sys import argv, exit
from oauth2client.file import Storage
from config import flask_config

from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from oauth2client import tools
import argparse
from script import backfill_blog, import_images

parser = argparse.ArgumentParser(parents=[tools.argparser])
FLAGS = parser.parse_args()

def authorize_google_calendar():

    FLOW = flow_from_clientsecrets(flask_config.INSTALLED_APP_SECRET_PATH,
                   scope='https://www.googleapis.com/auth/calendar')

    # Save the credentials file here for use by the app
    storage = Storage(flask_config.INSTALLED_APP_CREDENTIALS_PATH)
    run_flow(FLOW, storage, FLAGS)

def print_usage():
    print "Usage:"
    print "%s --authorize (-a)     Authorize the Google Calendar API Client" % argv[0]
    print "%s --backfill-blog (-b) Backfill blog posts from data/jekyll-posts" % argv[0]
    print "%s --import-images (-i) Import images from data/jekyll-images" % argv[0]

if __name__ == '__main__':
    if '--backfill-blog' in argv or '-b' in argv:
        backfill_blog.backfill_from_jekyll('data/jekyll-posts')
    elif '--import-images' in argv or '-i' in argv:
        import_images.import_from_directory('data/jekyll-images')
    else:
        authorize_google_calendar()
