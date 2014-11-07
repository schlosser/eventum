"""
.. module:: EditEventForm
    :synopsis: A form for editing an :class:`~app.models.Event`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app.forms import CreateEventForm
from app.forms.CreateEventForm import INVALID_SLUG
from app.forms.validators import UniqueEditEvent
from wtforms import StringField, BooleanField
from wtforms.validators import Regexp
from app.lib.regex import SLUG_REGEX

def EditEventForm(original, *args, **kwargs):
    """ Creates an edit form. Function closure w/ original to prevent problems
        
        :param Event original: the event being edited
    """
    class EditEventForm(CreateEventForm):
        """A form for editing an :class:`~app.models.Event`.

        This inherits from :class:`CreateEventForm`, changing that slugs should not
        check for uniqueness in the database.

        :ivar update_all: :class:`wtforms.fields.BooleanField` - True if all events
            should be modified in this update.
        """
        update_all = BooleanField('Update all', default=False)
        slug = StringField('Slug', [Regexp(SLUG_REGEX, message=INVALID_SLUG), UniqueEditEvent(original)]) 
    return EditEventForm(*args, **kwargs)
