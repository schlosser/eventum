"""
.. module:: base
    :synopsis: All routes on the ``base`` Blueprint, as well as error handlers,
        before and after request handlers, and context processors.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from common.error_handlers import error_handlers
from flask import current_app, request, redirect, render_template
import requests


def not_found(error):
    """Handle 404 errors."""
    print current_app.url_map
    print "hello"
    old_site_url = 'http://adicu.github.com' + request.path
    try:
        response = requests.head(old_site_url, allow_redirects=True)
        if response.status_code == 200:
            return redirect(old_site_url)
    except requests.exceptions.ConnectionError:
        pass

    return render_template('error/404.html'), 404

# Overwrite the 404 handler to implement this functionality
error_handlers['404'] = (404, not_found)
