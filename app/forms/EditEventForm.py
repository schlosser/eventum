"""
.. module:: EditEventForm
    :synopsis: A form for editing an :class:`~app.models.Event`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app.forms import CreateEventForm
from app.forms.CreateEventForm import INVALID_SLUG
from wtforms import StringField, BooleanField
from wtforms.validators import Regexp
from app.lib.regex import SLUG_REGEX


class EditEventForm(CreateEventForm):
    """A form for editing an :class:`~app.models.Event`.

    This inherits from :class:`CreateEventForm`, changing that slugs should not
    check for uniqueness in the database.

    :ivar update_all: :class:`wtforms.fields.BooleanField` - True if all events
        should be modified in this update.
    """
    update_all = BooleanField('Update all', default=False)
    slug = StringField('Slug', [Regexp(SLUG_REGEX, message=INVALID_SLUG)]) 

    def __init__(self, original, *args, **kwargs):
        super(EditEventForm, self).__init__(*args, **kwargs)
        self.original = original
        self.slug = StringField('Slug', [Regexp(SLUG_REGEX, message=INVALID_SLUG), 
                                         self.slug_verify])

    def slug_verify(self, form, field):
        if field.data != self.original.slug:
            unique_with_database(form, field)
