"""
.. module:: CreateEventForm
    :synopsis: A form for creating an :class:`~app.models.Event`.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from flask.ext.wtf import Form
from eventum.forms.fields import TimeField
from eventum.forms.CreateBlogPostForm import image_with_same_name
from wtforms import StringField, DateField, TextAreaField, BooleanField, \
    SelectField, IntegerField, RadioField
from wtforms.validators import Required, ValidationError, Optional, \
    NumberRange, Regexp, URL
from eventum.forms.validators import UniqueEvent
from eventum.lib.regex import Regex


SHORT_DESCRIPTION_PLACEHOLDER = ('Short Description.  This should be **one to '
                                 'two** sentences long.')
LONG_DESCRIPTION_PLACEHOLDER = ('Long Description.  This should be **four to '
                                'five** sentences.  Feel free to include '
                                '[links](http://adicu.com).')
INVALID_SLUG = 'Post slug should only contain numbers, letters and dashes.'
DATE_FORMAT = '%m/%d/%Y'


class CreateEventForm(Form):
    """A form for the creation of a :class:`~app.models.Event` object.

    :ivar title: :class:`wtforms.fields.StringField` - The title of the event.
    :ivar slug: :class:`wtforms.fields.StringField` - A unique url fragment for
        this blog post. This may only contain letters, numbers, and dashes
        (``-``).
    :ivar location: :class:`wtforms.fields.StringField` - The location of the
        event.
    :ivar start_date: :class:`wtforms.fields.DateField` - The date the event
        starts on.
    :ivar end_date: :class:`wtforms.fields.DateField` - The date the event
        ends on.
    :ivar start_time: :class:`TimeField` - The time the event starts.
    :ivar end_time: :class:`TimeField` - The time the event ends.
    :ivar is_recurring: :class:`wtforms.fields.BooleanField` - True if the
        event is recurring.
    :ivar frequency: :class:`wtforms.fields.SelectField` - The interval of the
        occurrence. Can only take the value ``"weekly"``.
    :ivar every: :class:`wtforms.fields.IntegerField` - The number of
        ``frequency`` units after which the event repeats. For example,
        ``frequency = "weekly"`` and ``every = 2`` indicates that the event
        occurs every two weeks.
    :ivar ends: :class:`wtforms.fields.RadioField` - ``"after"`` if the event
        ends after ``num_occurrences`` occurrences, or ``"on"`` if the date
        ends on ``recurrence_end_date``.
    :ivar num_occurrences: :class:`wtforms.fields.IntegerField` - The number of
        occurrences for a recurring event.  Should be set only if ``ends`` is
        set to ``"after"``.
    :ivar recurrence_end_date: :class:`wtforms.fields.DateField` - The date
        that the recurrence ends on.  Should be set only if ``ends`` is set to
        ``"on"``.
    :ivar recurrence_summary: :class:`wtforms.fields.StringField` - A plain
        English explanation of the recurrence. Generated in JavaScript but
        stored here.
    :ivar short_description: :class:`wtforms.fields.TextAreaField` - The
        markdown text of the short description for the event.
    :ivar long_description: :class:`wtforms.fields.TextAreaField` - The
        markdown text of the long description for the event.
    :ivar published: :class:`wtforms.fields.BooleanField` - True if the event
        is published.
    :ivar facebook_url: :class:`wtforms.fields.StringField` - The URL of the
        associated Facebook event.
    :ivar event_image: :class:`wtforms.fields.StringField` - The filename of
        the headline image.
    """

    title = StringField('Title',
                        [Required(message="Please provide an event title.")])
    slug = StringField('Slug', [UniqueEvent(),
                                Regexp(Regex.SLUG_REGEX,
                                       message=INVALID_SLUG)])
    location = StringField('Location')
    start_date = DateField('Start date', [Optional()], format=DATE_FORMAT)
    start_time = TimeField('Start time', [Optional()])
    end_date = DateField('End date', [Optional()], format=DATE_FORMAT)
    end_time = TimeField('End time', [Optional()])
    is_recurring = BooleanField('Is Recurring')
    frequency = SelectField('Repeats', choices=[('weekly', 'Weekly')],
                            default="weekly")
    every = IntegerField('Every', [NumberRange(min=1, max=30)], default=1)
    ends = RadioField('Ends', choices=[("after", "After"), ("on", "On")],
                      default="after")
    num_occurrences = IntegerField('Every', [NumberRange(min=1)], default=1)
    recurrence_end_date = DateField('Repeat End Date', [Optional()],
                                    format=DATE_FORMAT)
    recurrence_summary = StringField('Summary')
    short_description = TextAreaField('Short description',
                                      default=SHORT_DESCRIPTION_PLACEHOLDER)
    long_description = TextAreaField('Long description',
                                     default=LONG_DESCRIPTION_PLACEHOLDER)
    published = BooleanField('Published')
    facebook_url = StringField('Facebook  URL', [Optional(), URL()])
    event_image = StringField('Image', [image_with_same_name])

    def post_validate(self, validation_stopped):
        """Make sure that the start datetime comes before the end datetime.


        :param self: The form to validate
        :type self: :class:`Form`
        :param bool validation_stopped: True if any validator raised
            :class:`~wtforms.validators.StopValidation`.
        :raises: :class:`wtforms.validators.ValidationError`
        """
        if not validation_stopped:
            start_date = self.start_date.data
            start_time = self.start_time.data
            end_date = self.end_date.data
            end_time = self.end_time.data

            # Start and end dates should be in order.
            if start_date and end_date and start_date > end_date:
                raise ValidationError("Start date should come before end date")
            if (all([start_date, start_time, end_date, end_time]) and
                    start_time > end_time):
                raise ValidationError("Start time should come before end date")
