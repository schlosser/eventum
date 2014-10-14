import logging

from app import create_app, run
from config import flask_config

app = create_app()

if __name__ == "__main__":
    maxBytes = int(flask_config.LOG_FILE_MAX_SIZE) * 1024 * 1024
    appHandler = logging.handlers.RotatingFileHandler(flask_config.APP_LOG_FILENAME,
                                                      maxBytes=maxBytes)
    formatter = logging.Formatter("%(levelname)s @ %(asctime)s @ %(filename)s %(funcName)s %(lineno)d: %(message)s")
    appHandler.setLevel(logging.INFO)
    appHandler.setFormatter(formatter)

    accessHandler = logging.handlers.RotatingFileHandler(flask_config.WERKZEUG_LOG_FILENAME,
                                                         maxBytes=maxBytes)
    accessHandler.setLevel(logging.INFO)
    logging.getLogger("werkzeug").addHandler(accessHandler)

    app.logger.addHandler(appHandler)
    app.logger.info("Starting Server")
    run()
    app.logger.info("Closing Server")
