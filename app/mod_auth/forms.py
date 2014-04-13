from app.mod_auth.models import User
from flask.ext.wtf import Form
from wtforms import TextField, RadioField, HiddenField
from wtforms.validators import Required, Email, URL, ValidationError
from mongoengine.queryset import DoesNotExist, MultipleObjectsReturned

EMAIL_ERROR = 'Please provide a valid email address.'


class CreateProfileForm(Form):
    name = TextField('Full Name')
    email = TextField('Email Address', [Email(message=EMAIL_ERROR),
                                        Required(message=EMAIL_ERROR)])
    next = HiddenField('hidden', [URL(require_tld=False)])


class Unique(object):

    def __init__(self, message=None):
        if not message:
            message = u'A user with that email address already exists'
        self.message = message

    def __call__(self, form, field):
        try:
            User.objects.get(email=field.data)
            # If there isn't a DoesNotExist error, a user already exists
            raise ValidationError(self.message)
        except DoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise ValidationError(self.message)


class AddUserForm(Form):
    email = TextField('Email Address', [
        Email(message=EMAIL_ERROR), Required(message=EMAIL_ERROR),
        Unique()])
    user_type = RadioField('User Type', [
        Required(message="Please select a user type.")],
        [(1, "Editor"), (2, "Publisher"), (3, "Admin")])