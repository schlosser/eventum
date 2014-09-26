class GoogleCalendarAPIError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class GoogleCalendarAPIMissingID(GoogleCalendarAPIError):
    def __init__(self, message='This event was not assigned a gcal_id'):
        GoogleCalendarAPIError.__init__(self, message)

class GoogleCalendarAPIBadStatusLine(GoogleCalendarAPIError):
    def __init__(self, message='Encountered a Bad Status Line error with the API'):
        GoogleCalendarAPIError.__init__(self, message)

class GoogleCalendarAPIEventAlreadyDeleted(GoogleCalendarAPIError):
    def __init__(self, message='This event was deleted from Google Calendar'):
        GoogleCalendarAPIError.__init__(self, message)

class GoogleCalendarAPIErrorNotFound(GoogleCalendarAPIError):
    def __init__(self, uri, message='Got \'Not Found\' from Google Calendar: '):
        GoogleCalendarAPIError.__init__(self, message=message + uri)

