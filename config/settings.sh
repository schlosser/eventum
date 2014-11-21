#!/bin/sh


# ==========================================================
# Eventum
# ==========================================================

# Flask settings
export EVENTUM_HOST=localhost
export EVENTUM_PORT=5001
export EVENTUM_DEBUG=TRUE
export EVENTUM_SECRET_KEY=

# Cross-site request forgery settings
export EVENTUM_CSRF_ENABLED=TRUE
export EVENTUM_CSRF_SESSION_KEY=

# Google-related credentials
export EVENTUM_INSTALLED_APP_CLIENT_SECRET_PATH=client_secrets.json
export EVENTUM_CREDENTIALS_PATH=config/credentials.json
export EVENTUM_GOOGLE_AUTH_ENABLED=FALSE
export EVENTUM_CLIENT_SECRETS_PATH=config/client_secrets.json

# calendar settings
export EVENTUM_PRIVATE_CALENDAR_ID=
export EVENTUM_PUBLIC_CALENDAR_ID=

# mongo db settings
export EVENTUM_MONGO_DATABASE=eventum

# logging settings
export EVENTUM_LOG_FILE_MAX_SIZE=256  # in MB
export EVENTUM_APP_LOG_NAME=log/eventum_app.log
export EVENTUM_WERKZEUG_LOG_NAME=log/eventum_werkzeug.log

# ==========================================================
# Client
# ==========================================================

# Flask settings
export CLIENT_HOST=localhost
export CLIENT_PORT=5001
export CLIENT_DEBUG=TRUE
export CLIENT_SECRET_KEY=

# Cross-site request forgery settings
export CLIENT_CSRF_ENABLED=TRUE
export CLIENT_CSRF_SESSION_KEY=

# mongo db settings
export CLIENT_MONGO_DATABASE=eventum

# logging settings
export CLIENT_LOG_FILE_MAX_SIZE=256  # in MB
export CLIENT_APP_LOG_NAME=log/client_app.log
export CLIENT_WERKZEUG_LOG_NAME=log/client_werkzeug.log
