from __future__ import print_function, absolute_import

import argparse
import sys

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from oauth2client import tools

if len(sys.argv) < 3:
    msg = "eventum/authorize.py <CLIENT-SECRET-PATH> <CLIENT-CREDENTIALS-PATH>"
    sys.exit(msg)
else:
    client_secret_path = sys.argv[1]
    client_credentials_path = sys.argv[2]
    sys.argv.remove(client_secret_path)
    sys.argv.remove(client_credentials_path)

    parser = argparse.ArgumentParser(parents=[tools.argparser])

    FLAGS = parser.parse_args()
    SCOPE = 'https://www.googleapis.com/auth/calendar'

    FLOW = flow_from_clientsecrets(
        client_secret_path,
        scope=SCOPE)

    # Save the credentials file here for use by the app
    storage = Storage(client_credentials_path)
    run_flow(FLOW, storage, FLAGS)
