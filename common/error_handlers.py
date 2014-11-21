"""
.. module:: error_handlers
    :synopsis: All of the error handlers for flask applications

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

import sys
from flask import render_template, request, current_app


def exception_handler(error):
    """Handle uncaught exceptions."""
    current_app.logger.error("Uncaught Exception", exc_info=sys.exc_info())
    current_app.handle_exception(error)  # default error handler


def bad_request(error):
    """Handle 400 errors."""
    return render_template('error/400.html'), 400


def not_authorized(error):
    """Handle 401 errors."""
    return render_template('error/401.html'), 401


def forbidden(error):
    """Handle 403 errors."""
    return render_template('error/403.html'), 403


def not_found(error):
    """Handle 404 errors."""
    return render_template('error/404.html'), 404


def method_not_allowed(error):
    """Handle 405 errors."""
    return render_template('error/405.html', method=request.method), 405


def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('error/500.html'), 500

error_handlers = {
    'Exception': (Exception, exception_handler),
    '400': (400, bad_request),
    '401': (401, not_authorized),
    '403': (403, forbidden),
    '404': (404, not_found),
    '405': (405, method_not_allowed),
    '500': (500, internal_server_error)
}
