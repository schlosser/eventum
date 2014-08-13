class GoogleCalendarAPIError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class GoogleCalendarAPIMissingID(GoogleCalendarAPIError):
    def __init__(self, message='This event was not assigned a gcal_id'):
        GoogleCalendarAPIError.__init__(self, message)