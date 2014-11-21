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
    """ Creates an edit form.
    
    Uses a function closure to pass ``original`` into the UniqueEditEvent
    validator for EditEventForm.slug
        
    :param Event original: the event being edited
    """
    class EditEventForm(CreateEventForm):
        """A form for editing an :class:`~app.models.Event`.

        This inherits from :class:`CreateEventForm`. Edited slugs are checked
        for uniqueness, while unedited slugs are not (they should appear once
        in the database).

        :ivar update_all: :class:`wtforms.fields.BooleanField` - True if all
            events should be modified in this update.
        :ivar slug: :class:`wtforms.fields.StringField` - Unique url fragment 
            for the blog post. It may only contain letters, numbers, and dashes
            (``-``).
        """
        update_all = BooleanField('Update all', default=False)
        slug = StringField('Slug', [Regexp(SLUG_REGEX, message=INVALID_SLUG),
                                    UniqueEditEvent(original)])
    return EditEventForm(*args, **kwargs)
