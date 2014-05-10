from app.auth.models import Whitelist
from flask.ext.wtf import Form
from wtforms import TextField, RadioField, HiddenField
from wtforms.validators import Required, Email, URL, ValidationError

EMAIL_ERROR = 'Please provide a valid email address.'


class Unique(object):

    def __init__(self, message=None):
        if not message:
            message = u'A user with that email address already exists'
        self.message = message

    def __call__(self, form, field):
        if Whitelist.objects(email=field.data).count() != 0:
            raise ValidationError(self.message)

class CreateProfileForm(Form):
    name = TextField('Full Name')
    email = TextField('Email Address',
                      [Email(message=EMAIL_ERROR), Required(message=EMAIL_ERROR)])
    next = HiddenField('hidden', [URL(require_tld=False)])


class AddToWhitelistForm(Form):
    email = TextField('Email Address',
                      [Email(
                          message=EMAIL_ERROR), Required(message=EMAIL_ERROR),
                       Unique()])
    user_type = RadioField('User Type',
                           [Required(message="Please select a user type.")],
                           choices=[("user", "User"), ('editor', "Editor"),
                                    ('publisher', "Publisher"), ('admin', "Admin")])
