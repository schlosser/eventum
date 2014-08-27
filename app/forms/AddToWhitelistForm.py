from app.models import Whitelist
from flask.ext.wtf import Form
from wtforms import StringField, RadioField
from wtforms.validators import Required, Email, ValidationError, Optional
from app.forms.validators import image_with_same_name

EMAIL_ERROR = 'Please provide a valid email address.'


class Unique(object):

    def __init__(self, message=None):
        if not message:
            message = u'A user with that email address already exists'
        self.message = message

    def __call__(self, form, field):
        if form.user_type.data != 'fake_user' and \
                Whitelist.objects(email=field.data).count() != 0:
            raise ValidationError(self.message)


class AddToWhitelistForm(Form):
    email = StringField('Email Address',
                      [Email(message=EMAIL_ERROR),
                       Optional(),
                       Unique()])
    name = StringField('Name', [])
    fake_user_image = StringField('Image', [image_with_same_name])
    user_type = RadioField('User Type',
                           [Required(message="Please select a user type.")],
                           choices=[('editor', "Editor"),
                                    ('publisher', "Publisher"),
                                    ('admin', "Admin"),
                                    ("fake_user", "Fake User")])