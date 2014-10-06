#!/bin/sh

# flask settings
export HOST=localhost
export PORT=5000
export DEBUG=TRUE
export SECRET_KEY=

# google related credentials
export INSTALLED_APP_CLIENT_SECRET_PATH=client_secrets.json
export CREDENTIALS_PATH=config/credentials.json
export GOOGLE_AUTH_ENABLED=FALSE
export CLIENT_SECRETS_PATH=config/client_secrets.json

# Cross-site request forgery settings
export CSRF_ENABLED=TRUE
export CSRF_SESSION_KEY=

# calendar settings
export PRIVATE_CALENDAR_ID=
export PUBLIC_CALENDAR_ID=

# mongo db settings
export MONGO_DATABASE=eventum

