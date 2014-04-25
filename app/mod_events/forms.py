import datetime, time
from flask.ext.wtf import Form
from wtforms import TextField, DateField, TextAreaField, Field, widgets
from wtforms.validators import Required, ValidationError


class TimeField(Field):
    """A text field which stores a `datetime.time` object.

    Accepts time string in multiple formats: 20:10, 20:10:00, 10:00 am,
    9:30pm, etc. Taken from
    http://flask-admin.readthedocs.org/en/v1.0.7/_modules/flask/ext/admin
        /form/fields/#TimeField
    """
    widget = widgets.TextInput()

    def __init__(self, label, validators=None, formats=None, **kwargs):
        """Constructor

        :param label:
            Label
        :param validators:
            Field validators
        :param formats:
            Supported time formats, as a enumerable.
        :param kwargs:
            Any additional parameters
        """
        super(TimeField, self).__init__(label, validators, **kwargs)
        print "hello?"
        self.formats = formats or ('%H:%M:%S', '%H:%M',
                                  '%I:%M:%S%p', '%I:%M%p',
                                  '%I:%M:%S %p', '%I:%M %p')

    def _value(self):
        if self.raw_data:
            return u' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.format) or u''

    def process_formdata(self, valuelist):
        if valuelist:
            print valuelist
            date_str = u' '.join(valuelist)

            for format in self.formats:
                try:
                    timetuple = time.strptime(date_str, format)
                    self.data = datetime.time(timetuple.tm_hour,
                                              timetuple.tm_min,
                                              timetuple.tm_sec)
                    return
                except ValueError:
                    pass

            raise ValueError('Invalid time format')


class CreateEventForm(Form):
    title = TextField('Title', [
        Required(message="Please provide an event title.")])
    location = TextField('Location')
    start_date = DateField('Start date')
    start_time = TimeField('Start time')
    end_date = DateField('End date')
    end_time = TimeField('End time')
    short_description = TextAreaField('Short description')
    long_description = TextAreaField('Long description')

    def post_validate(form, validation_stopped):
        """"""
        start_date = form.start_date.data
        start_time = form.start_time.data
        end_date = form.end_date.data
        end_time = form.end_time.data

        # Start datetime should come before end datetime
        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = datetime.datetime.combine(end_date, end_time)
        if start_datetime > end_datetime:
            raise ValidationError("Start date should come before end date")



