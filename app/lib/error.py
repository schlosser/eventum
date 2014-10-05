"""
.. module:: error
    :synopsis: Errors to be raised in the app.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

class GoogleCalendarAPIError(Exception):
    """Something went wrong with Google Calendar."""
    DEFAULT_MESSAGE = 'Something went wrong with Google Calendar.'

    def __init__(self, message=None):
        if not message:
            message = self.DEFAULT_MESSAGE
        Exception.__init__(self, message)


class GoogleCalendarAPIMissingID(GoogleCalendarAPIError):
    """This event was not assigned a gcal_id"""

    DEFAULT_MESSAGE = 'This event was not assigned a gcal_id'


class GoogleCalendarAPIBadStatusLine(GoogleCalendarAPIError):
    """Encountered a Bad Status Line error with the API"""

    DEFAULT_MESSAGE = 'Encountered a Bad Status Line error with the API'


class GoogleCalendarAPIEventAlreadyDeleted(GoogleCalendarAPIError):
    """Encountered a Bad Status Line error with the API"""

    DEFAULT_MESSAGE = 'This event was deleted from Google Calendar'


class GoogleCalendarAPIErrorNotFound(GoogleCalendarAPIError):
    """Got 'Not Found' from Google Calendar"""

    DEFAULT_MESSAGE = 'Got \'Not Found\' from Google Calendar: '

    def __init__(self, uri, message=None):
        if not message:
            message = self.DEFAULT_MESSAGE + uri
        GoogleCalendarAPIError.__init__(self, message=message)

