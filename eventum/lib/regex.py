"""
.. module:: regex
    :synopsis: Regexes to be used around the app.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from flask import current_app
from eventum.config import eventum_config


class _LiveRegexCollection(object):

    SLUG_REGEX = r'[0-9a-zA-Z-]+'
    FILENAME_REGEX = r'[\w\-@\|\(\)]+'

    @property
    def FULL_FILENAME_REGEX(self):
        return "{fname}({ext})".format(
            fname=self.FILENAME_REGEX,
            ext="|".join(
                eventum_config.EVENTUM_ALLOWED_UPLOAD_EXTENSIONS))

    @property
    def EXTENSION_REGEX(self):
        return "|".join(
            eventum_config.EVENTUM_ALLOWED_UPLOAD_EXTENSIONS)

    @property
    def VALID_PATHS(self):
        return r'^({}|http://|https://).*$'.format(
            current_app.config['EVENTUM_BASEDIR'])


Regex = _LiveRegexCollection()
