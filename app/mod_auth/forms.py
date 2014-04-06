from app import mongo
from app.mod_auth.models import Editor, Publisher, Admin
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, RadioField
from wtforms.validators import Required, Email, EqualTo, ValidationError

EMAIL_ERROR = 'Please provide a valid email address.'


class LoginForm(Form):
    email = TextField('Email Address', [Email(message=EMAIL_ERROR),
                                        Required(message=EMAIL_ERROR)])
    password = PasswordField('Password', [
        Required(message='Please enter your password')])


class Unique(object):

    def __init__(self, message=None):
        if not message:
            message = u'A user with that email address already exists'
        self.message = message

    def __call__(self, form, field):
        if mongo.users.find_one({"email": field.data}):
            raise ValidationError(self.message)


class AddUserForm(Form):
    first_name = TextField('First Name')
    last_name = TextField('Last Name')
    email = TextField('Email Address', [
        Email(message=EMAIL_ERROR), Required(message=EMAIL_ERROR),
        Unique()])
    password = PasswordField('Temporary Password', [
        Required(message='Please choose a password.')])
    user_type = RadioField('User Type', [
        Required(message="Please select a user type.")],
        [(Editor, "Editor"), (Publisher, "Publisher"), (Admin, "Admin")])


class ChangePasswordForm(Form):
    old_password = PasswordField('Old Password')
    password = PasswordField('New Password', [
        Required(message='Please choose a new password')])
    password_confirm = PasswordField('Confirm New Password', [
        Required(message='Please confirm your new password'),
        EqualTo(password, message='Passwords do not match, please try again.'),
    ])
