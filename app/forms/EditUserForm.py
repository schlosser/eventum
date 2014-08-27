from flask.ext.wtf import Form
from wtforms import TextField, RadioField
from wtforms.validators import Required, Email

EMAIL_ERROR = 'Please provide a valid email address.'

class EditUserForm(Form):
    """"""
    name = TextField('Full Name', [Required("Please type a name")])
    email = TextField('Email Address',
                      [Email(message=EMAIL_ERROR),
                       Required(message=EMAIL_ERROR)])
    image_url = TextField('Image URL')
    user_type = RadioField('User Type',
                           [Required(message="Please select a user type.")],
                           choices=[('editor', "Editor"),
                                    ('publisher', "Publisher"),
                                    ('admin', "Admin"),
                                    ("fake_user", "Fake User")])