from flask.ext.wtf import Form
from wtforms import TextField, RadioField, HiddenField
from wtforms.validators import Required, Email, URL, ValidationError

class CreateUserForm(Form):
    """"""
    name = TextField('Full Name', [Required("Please type a name")])
    email = TextField('Email Address')
    user_type = RadioField('User Type',
                           [Required(message="Please select a user type.")],
                           choices=[("user", "User"), ('editor', "Editor"),
                                    ('publisher', "Publisher"), ('admin', "Admin")])