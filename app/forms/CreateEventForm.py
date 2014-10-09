"""
.. module:: CreateEventForm
    :synopsis: A form for creating an :class:`~app.models.Event`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask.ext.wtf import Form
from app.forms.fields import TimeField
from app.forms.CreateBlogPostForm import image_with_same_name
from wtforms import StringField, DateField, TextAreaField, BooleanField, \
    SelectField, IntegerField, RadioField
from wtforms.validators import Required, ValidationError, Optional, \
    NumberRange, Regexp, URL
from app.forms.validators import UniqueEvent


SHORT_DESCRIPTION_PLACEHOLDER = ('Short Description.  This should be **one to '
                                 'two** sentences long.')
LONG_DESCRIPTION_PLACEHOLDER = ('Long Description.  This should be **four to '
                                'five** sentences.  Feel free to include '
                                '[links](http://adicu.com).')
INVALID_SLUG = 'Post slug should only contain numbers, letters and dashes.'


class CreateEventForm(Form):
    """A form for the creation of a :class:`~app.models.Event` object.

    :ivar title: :class:`StringField` - The title of the event.
    :ivar slug: :class:`StringField` - A unique url fragment for this blog post.
        This may only contain letters, numbers, and dashes (``-``).
    :ivar location: :class:`StringField` - The location of the event.
    :ivar start_date: :class:`DateField` - The date the event starts on.
    :ivar end_date: :class:`DateField` - The date the event ends on.
    :ivar start_time: :class:`TimeField` - The time the event starts.
    :ivar end_time: :class:`TimeField` - The time the event ends.
    :ivar is_recurring: :class:`BooleanField` - True if the event is recurring.
    :ivar frequency: :class:`SelectField` - The interval of the occurrence. Can
        only take the value ``"weekly"``.
    :ivar every: :class:`IntegerField` - The number of ``frequency`` units
        after which the event repeats. For example, ``frequency = "weekly"``
        and ``every = 2`` indicates that the event occurs every two weeks.
    :ivar ends: :class:`RadioField` - ``"after"`` if the event ends after
        ``num_occurrences`` occurrences, or ``"on"`` if the date ends on
        ``recurrence_end_date``.
    :ivar num_occurrences: :class:`IntegerField` - The number of occurrences
        for a recurring event.  Should be set only if ``ends`` is set to
        ``"after"``.
    :ivar recurrence_end_date: :class:`DateField` - The date that the
        recurrence ends on.  Should be set only if ``ends`` is set to ``"on"``.
    :ivar recurrence_summary: :class:`StringField` - A plain English
        explanation of the recurrence. Generated in JavaScript but stored here.
    :ivar short_description: :class:`TextAreaField` - The markdown text of the
        short description for the event.
    :ivar long_description: :class:`TextAreaField` - The markdown text of the
        long description for the event.
    :ivar published: :class:`BooleanField` - True if the event is published.
    :ivar facebook_url: :class:`StringField` - The URL of the associated
        Facebook event.
    :ivar event_image: :StringField: - The filename of the headline image.
    """

    title = StringField('Title', [
        Required(message="Please provide an event title.")])
    slug = StringField('Slug',
                       [UniqueEvent(), Regexp('([0-9]|[a-z]|[A-Z]|-)*',
                                              message=INVALID_SLUG)])
    location = StringField('Location')
    start_date = DateField('Start date', [Optional()], format='%m/%d/%Y')
    start_time = TimeField('Start time', [Optional()])
    end_date = DateField('End date', [Optional()], format='%m/%d/%Y')
    end_time = TimeField('End time', [Optional()])
    is_recurring = BooleanField('Is Recurring')
    frequency = SelectField('Repeats',
                            choices=[('weekly', 'Weekly')],
                            default="weekly")
    every = IntegerField('Every', [NumberRange(min=1, max=30)], default=1)
    ends = RadioField('Ends',
                      choices=[("after", "After"),("on", "On")],
                      default="after")
    num_occurrences = IntegerField('Every', [NumberRange(min=1)], default=1)
    recurrence_end_date = DateField('Repeat End Date',
                                    [Optional()],
                                    format='%m/%d/%Y')
    recurrence_summary = StringField('Summary')
    short_description = TextAreaField('Short description',
                                      default=SHORT_DESCRIPTION_PLACEHOLDER)
    long_description = TextAreaField('Long description',
                                     default=LONG_DESCRIPTION_PLACEHOLDER)
    published = BooleanField('Published')
    facebook_url = StringField('Facebook  URL', [Optional(), URL()])
    event_image = StringField('Image', [image_with_same_name])

    def post_validate(form, validation_stopped):
        """Make sure that the start datetime comes before the end datetime.


        :param form: The form to validate
        :type form: :class:`Form`
        :param bool validation_stopped: True if any validator raised
            :class:`~wtforms.validators.StopValidation`.
        :raises: :exc:`ValidationError`
        """
        if not validation_stopped:
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
