from app.forms import CreateEventForm
from wtforms import StringField
from wtforms.validators import Regexp

class EditEventForm(CreateEventForm):
    slug = StringField('Slug', [Regexp('([0-9]|[a-z]|[A-Z]|-)*',
                                       message="Post slug should only contain numbers, letters and dashes.")])