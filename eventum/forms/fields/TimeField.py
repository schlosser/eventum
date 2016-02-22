"""
.. module:: TimeField
    :synopsis: A :mod:`wtforms` custom field that stores a
        :class:`datetime.date` as a string.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import datetime
import time
from wtforms import Field
from wtforms.widgets.html5 import TimeInput


class TimeField(Field):
    """A text field which stores a `datetime.time` matching a format.

    Adapted from:
    http://flask-admin.readthedocs.org/en/v1.0.7/_modules/flask/ext/admin/form/fields/#TimeField
    """
    widget = TimeInput()
    error_msg = 'Not a valid time.'

    def __init__(self,
                 label=None,
                 validators=None,
                 format='%I:%M%p',  # 1:45PM
                 **kwargs):
        """Creates a TimeField instance.

        :param str label: A label to be optionally displayed next to the field.
        :param validators: callables that validate the field's data.
        :type validators: list of functions or :class:`wtforms.validators`
        :param str format: the format to store the time in.
        """
        super(TimeField, self).__init__(label, validators, **kwargs)
        self.format = format

    def _value(self):
        """Called by :mod:`wtforms` to get the data from the field.

        :returns: The time encoded as a string.
        :rtype: str
        """
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        """Called by :mod:`wtforms`."""
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                self.data = datetime.time(
                    *time.strptime(time_str.lower(), self.format)[3:5]
                )
            except ValueError:
                self.data = None
                raise ValueError(self.gettext(self.error_msg))
