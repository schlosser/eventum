from mongoengine.fields import DateTimeField
from datetime import datetime, date

class DateField(DateTimeField):
    """A datetime.date field.

    Looks to the outside world like a datatime.date, but functions
    as a datetime.datetime object in the database.s
    """

    def to_python(self, value):
        """Convert from datetime.datetime to datetime.date."""
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        raise ValueError("Unkown type '%r' of variable %r",type(value), value)
