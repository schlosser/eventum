"""
.. module:: EditEventForm
    :synopsis: A form for editing an :class:`~app.models.Event`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app.forms import CreateEventForm
from wtforms import StringField
from wtforms.validators import Regexp

class EditEventForm(CreateEventForm):
    """A form for editing an :class:`~app.models.Event`.

    This inherits from :class:`CreateEventForm`, changing only that slugs
    """
    slug = StringField('Slug', [Regexp('([0-9]|[a-z]|[A-Z]|-)*',
                                       message="Post slug should only contain numbers, letters and dashes.")])