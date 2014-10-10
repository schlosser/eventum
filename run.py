import logging
import sys
import traceback

from app import create_app, run

app = create_app()

@app.errorhandler(Exception)
def exceptionHandler(error):
    app.logger.error("Uncaught Exception", exc_info=sys.exc_info()) 
    app.handle_exception(error) # default error handler

if __name__ == "__main__":
    maxBytes = 1024 * 1024 * 256    # cap files at 256 MB (should we?)
    appHandler = logging.handlers.RotatingFileHandler("log/app.log",
                                                      maxBytes=maxBytes)
    formatter = logging.Formatter("%(levelname)s @ %(asctime)s @ %(filename)s %(funcName)s %(lineno)d: %(message)s")
    appHandler.setLevel(logging.INFO)
    appHandler.setFormatter(formatter)

    accessHandler = logging.handlers.RotatingFileHandler("log/werkzeug.log",
                                                         maxBytes=maxBytes)
    accessHandler.setLevel(logging.INFO)
    logging.getLogger("werkzeug").addHandler(accessHandler)

    app.logger.addHandler(appHandler)
    app.logger.info("Starting Server")
    run()
    app.logger.info("Closing Server")
