from app.forms import CreateEventForm
from app.forms.CreateEventForm import unique_with_database
from wtforms import StringField
from wtforms.validators import Regexp

class EditEventForm(CreateEventForm):
    slug = StringField('Slug', [Regexp('([0-9a-zA-Z-])*',
                                       message="Post slug should only contain numbers, letters and dashes."),
                                self.slug_verify])
    def __init__(self, event, *args, **kwargs):
        super(EditEventForm, self).__init__(*args, **kwargs)
        self.event = event
    def slug_verify(self, form, field):
        if field.data != self.event.slug:
            unique_with_database(form, field)
