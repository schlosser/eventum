"""
.. module:: TimeField
    :synopsis: A :mod:`mongoengine` custom field that stores a
        :class:`datetime.time` object as an int / float in seconds.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from mongoengine.base import BaseField
from datetime import time

class TimeField(BaseField):
    """A datetime.time field.

    Looks to the outside world like a datatime.time, but stores in the
    database as an int/float number of seconds since midnight.
    """

    def validate(self, value):
        """Called by :mod:`mongoengine` to validate the field.

        Only accepts a datetime.time, or a int/float number of seconds
        since midnight.

        :param value: The value to validate (and later store).
        :type value: int, float, or :class:`datetime.time`.
        """
        if not isinstance(value, (time, int, float)):
            self.error(u'cannot parse time: %r' % value)

    def to_mongo(self, value):
        """Called by :mod:`mongoengine` to convert ``value`` to the value it
        will be stored as in Mongo.

        This is a wrapper on top of :method:`prepare_query_value`.

        :param value: The value to validate (and later store).
        :type value: int, float, or :class:`datetime.time`.
        :returns: ``value``, ready to be stored in Mongo.
        :rtype: int or float
        """
        return self.prepare_query_value(None, value)

    def to_python(self, value):
        """Called by :mod:`mongoengine` to convert ``value`` into the outward-
        facing value for this field.

        Converts the int/float number of seconds since midnight to a
        time.

        :param value: The value from Mongo.
        :type value: :class:`datetime.time`.
        :returns: ``value``, converted to :class:`datetime.time`.
        :rtype: :class:`datetime.time`
        """
        if isinstance(value, (int, float)):
            value = int(value)
            return time(hour=value/3600, minute=value%3600/60, second=value%60)
        return value

    def prepare_query_value(self, op, value):
        """Convert from datetime.time to int/float number of seconds, if
        needed.

        :param value: The value to validate (and later store).
        :type value: int, float, or :class:`datetime.time`.
        :returns: ``value``, ready to be stored in Mongo.
        :rtype: int or float
        """
        if value is None:
            return value
        if isinstance(value, time):
            return value.hour * 3600 + \
                   value.minute * 60 + \
                   value.second + \
                   value.microsecond / 1000000
        if isinstance(value, (int, float)):
            return value
