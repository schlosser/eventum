from mongoengine.base import BaseField
from datetime import time

class TimeField(BaseField):

    """A datetime.time field.

    Looks to the outside world like a datatime.time, but stores in the
    database as an int/float number of seconds since midnight.
    """

    def validate(self, value):
        """Only accepts a datetime.time, or a int/float number of seconds
        since midnight.
        """
        if not isinstance(value, (time, int, float)):
            self.error(u'cannot parse time "%r"' % value)

    def to_mongo(self, value):
        """Wrapper on top of prepare_query_value"""
        return self.prepare_query_value(None, value)

    def to_python(self, value):
        """Convert the int/float number of seconds since midnight to a
        time"""
        if isinstance(value, (int, float)):
            value = int(value)
            return time(hour=value/3600, minute=value%3600/60, second=value%60)
        return value

    def prepare_query_value(self, op, value):
        """Convert from datetime.time to int/float number of seconds."""
        if value is None:
            return value
        if isinstance(value, time):
            return value.hour * 3600 + \
                   value.minute * 60 + \
                   value.second + \
                   value.microsecond / 1000000
        if isinstance(value, (int, float)):
            return value

    def __nonzero__(self):
        """Defining all TimeField instances to be truthy avoids a problem where
        TimeField instances representing midnight (00:00) are falsey.
        """
        return True