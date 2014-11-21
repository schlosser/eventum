"""
.. module:: DateField
    :synopsis: A :mod:`mongoengine` custom field that stores a
        :class:`datetime.date` object as a :class:`datetime.datetime`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""


from mongoengine.fields import DateTimeField
from datetime import datetime, date

class DateField(DateTimeField):
    """A datetime.date field.

    Looks to the outside world like a ``datatime.date``, but functions
    as a ``datetime.datetime`` object in the database.
    """

    def to_python(self, value):
        """Convert from :class:``datetime.datetime`` to
        :class:``datetime.date``.

        This overwrites the :class:`mongoengine.fields.DateTimeField`` method for
        accessing the value of this field.

        :param value: The date from mongo
        :type value: :class:`datetime.datetime` or :class:`datetime.date`
        :returns: The same date
        :rtype: :class:`datetime.date`
        :raises: ValueError
        """
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        raise ValueError("Unkown type '%r' of variable %r",type(value), value)
