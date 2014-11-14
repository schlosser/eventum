"""
.. module:: AddToWhitelistForm
    :synopsis: A form to whitelist an email address for account creation.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask.ext.wtf import Form
from wtforms import StringField, RadioField
from wtforms.validators import Required, Email, Optional
from app.forms.validators import image_with_same_name, UniqueEmail

EMAIL_ERROR = 'Please provide a valid email address.'


class AddToWhitelistForm(Form):
    """A form for the creation of a :class:`Whitelist` entry.

    There are four options for ``user_type``:

    - Editor (``"editor"``): Can edit content on Eventum.
    - Publisher (``"publisher"``) Can publish content to the client.
    - Admin (``"publisher"``) Can manage user accounts and permissions.
    - Fake User (``"fake_user"``) Can not do anything, and should only be used as
        dummy accounts for guest blog posts.

    If the whitelisted user is a fake user (``user_type`` is set to
    ``fake_user``) then ``name`` and ``fake_user_image`` must also be set.
    Otherwise, these fields may be omitted.

    :ivar email: :class:`wtforms.fields.StringField` - The email address to be
        whitelisted
    :ivar name: :class:`wtforms.fields.StringField` - The name of the user to
        whitelist (fake users only)
    :ivar fake_user_image: :class:`wtforms.fields.StringField` - A URL to a
        profile picture (fake users only)
    :ivar user_type: :class:`wtforms.fields.RadioField` - The permission level
        for the user.
    """
    email = StringField('Email Address', [Email(message=EMAIL_ERROR),
                                          Optional(),
                                          UniqueEmail()])
    name = StringField('Name', [])
    fake_user_image = StringField('Image', [image_with_same_name])
    user_type = RadioField('User Type',
                           [Required(message="Please select a user type.")],
                           choices=[('editor', "Editor"),
                                    ('publisher', "Publisher"),
                                    ('admin', "Admin"),
                                    ("fake_user", "Fake User")])
