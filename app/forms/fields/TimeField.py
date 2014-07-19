import datetime
import time
from wtforms import Field
from wtforms.widgets.html5 import TimeInput

class TimeField(Field):
    """
    A text field which stores a `datetime.time` matching a format.

    Taken from
    http://flask-admin.readthedocs.org/en/v1.0.7/_modules/flask/ext/admin
        /form/fields/#TimeField
    """
    widget = TimeInput()
    error_msg = 'Not a valid time.'

    def __init__(self, label=None, validators=None, format='%I:%M%p', **kwargs):
        super(TimeField, self).__init__(label, validators, **kwargs)
        print kwargs
        self.format = format

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                self.data = datetime.time(
                    *time.strptime(time_str.lower(), self.format)[3:5]
                )
            except ValueError:
                self.data = None
                raise ValueError(self.gettext(self.error_msg))