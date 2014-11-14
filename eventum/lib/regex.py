"""
.. module:: regex
    :synopsis: Regexes to be used around the app.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from config.flask_config import ALLOWED_UPLOAD_EXTENSIONS

SLUG_REGEX = r'([0-9]|[a-z]|[A-Z]|\-)+'
FILENAME_REGEX = r'[\w\-@\|\(\)]+'
FULL_FILENAME_REGEX = ( FILENAME_REGEX + '(' + 
                       ('|'.join(ALLOWED_UPLOAD_EXTENSIONS)+')'))