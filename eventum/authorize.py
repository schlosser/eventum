import eventum
import argparse
from sys import argv

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from oauth2client import tools

if len(argv) < 3:
    print "eventum/authorize.py <CLIENT-SECRET-PATH> <CLIENT-CREDENTIALS-PATH>"
else:
    client_secret_path = argv[1]
    client_credentials_path = argv[2]
    argv.remove(client_secret_path)
    argv.remove(client_credentials_path)

    parser = argparse.ArgumentParser(parents=[tools.argparser])

    FLAGS = parser.parse_args()
    SCOPE = 'https://www.googleapis.com/auth/calendar'

    FLOW = flow_from_clientsecrets(
        client_secret_path,
        scope=SCOPE)

    # Save the credentials file here for use by the app
    storage = Storage(client_credentials_path)
    run_flow(FLOW, storage, FLAGS)
