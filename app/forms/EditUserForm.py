"""
.. module:: EditUserForm
    :synopsis: A form for editing a :class:`~app.models.User`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask.ext.wtf import Form
from wtforms import StringField, RadioField
from wtforms.validators import Required, Email

EMAIL_ERROR = 'Please provide a valid email address.'

class EditUserForm(Form):
    """A form for editing a :class:`~app.models.User`.

    :ivar name: :class:`StringField` - The user's name
    :ivar email: :class:`StringField` - The user's email address
    :ivar image_url: :class:`StringField` - A URL to a profile picture
    :ivar user_type: :class:`RadioField` - The permission level for the user.
    """
    name = StringField('Full Name', [Required("Please type a name")])
    email = StringField('Email Address',
                      [Email(message=EMAIL_ERROR),
                       Required(message=EMAIL_ERROR)])
    image_url = StringField('Image URL')
    user_type = RadioField('User Type',
                           [Required(message="Please select a user type.")],
                           choices=[('editor', "Editor"),
                                    ('publisher', "Publisher"),
                                    ('admin', "Admin"),
                                    ("fake_user", "Fake User")])