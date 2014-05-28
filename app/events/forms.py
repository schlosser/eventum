import datetime, time
from flask.ext.wtf import Form
from wtforms import TextField, DateField, TextAreaField, Field, BooleanField, \
    SelectField, IntegerField, RadioField
from wtforms.validators import Required, ValidationError, Optional, \
    NumberRange
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


class CreateEventForm(Form):

    title = TextField('Title', [
        Required(message="Please provide an event title.")])
    location = TextField('Location')
    start_date = DateField('Start date', [Optional()], format='%m/%d/%Y')
    start_time = TimeField('Start time', [Optional()])
    end_date = DateField('End date', [Optional()], format='%m/%d/%Y')
    end_time = TimeField('End time', [Optional()])
    repeat = BooleanField('Repeat')
    frequency = SelectField('Repeats', choices=[('weekly', 'Weekly')],
                            default="weekly")
    every = IntegerField('Every', [NumberRange(min=1, max=30)], default=1)
    ends = RadioField('Ends', choices=[
        ("after", "After"),
        ("on", "On")
    ], default="after")
    num_occurances = IntegerField('Every', [NumberRange(min=1)], default=1)
    repeat_end_date = DateField('Repeat End Date', [Optional()],
                                format='%m/%d/%Y')
    summary = TextField('Summary')
    short_description = TextAreaField('Short description')
    long_description = TextAreaField('Long description')
    published = BooleanField('Published')
    update_all = BooleanField('Update all', default=False)
    update_following = BooleanField('Update Following', default=False)

    def post_validate(form, validation_stopped):
        """Make sure that the start datetime comes before the end datetime"""
        start_date = form.start_date.data
        start_time = form.start_time.data
        end_date = form.end_date.data
        end_time = form.end_time.data

        # Start and end dates should be in order.
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date should come before end date")
        if all([start_date, start_time, end_date, end_time]) and \
                start_time > end_time:
            raise ValidationError("Start time should come before end date")

class DeleteEventForm(Form):

    delete_all = BooleanField('Delete All', default=False)
    delete_following = BooleanField('Delete Following', default=False)

