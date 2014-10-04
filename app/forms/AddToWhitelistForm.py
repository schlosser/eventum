"""
.. module:: AddToWhitelistForm
    :synopsis: A form to whitelist an email address for account creation.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""


from app.models import Whitelist
from flask.ext.wtf import Form
from wtforms import StringField, RadioField
from wtforms.validators import Required, Email, ValidationError, Optional
from app.forms.validators import image_with_same_name

EMAIL_ERROR = 'Please provide a valid email address.'


class UniqueEmail(object):
    """A validator that verifies whether or not an email address is unique in
    the :class:`Whitelist` collection.
    """

    DEFAULT_MESSAGE = 'A user with that email address already exists'

    def __init__(self, message=None):
        """Ensures unique emails are unique in the :class:`Whitelist`
        collection.

        :param str message: An alternate message to be raised.
        """
        if not message:
            message = self.DEFAULT_MESSAGE
        self.message = message

    def __call__(self, form, field):
        """Called internally by :mod:`wtforms` on validation of the field.

        :param form: The parent form
        :type form: :class:`Form`
        :param field: The field to validate
        :type field: :class:`Field`
        :raises: :exc:`ValidationError`
        """
        if form.user_type.data != 'fake_user' and \
                Whitelist.objects(email=field.data).count() != 0:
            raise ValidationError(self.message)


class AddToWhitelistForm(Form):
    """A form for the creation of a :class:`Whitelist` entry.

    There are four options for ``user_type``:

    - Editor (``editor``): Can edit content on Eventum.
    - Publisher (``publisher``) Can publish content to the client.
    - Admin (``publisher``) Can manage user accounts and permissions.
    - Fake User (``fake_user``) Can not do anything, and should only be used as
        dummy accounts for guest blog posts.

    If the whitelisted user is a fake user (``user_type`` is set to
    ``fake_user``) then ``name`` and ``fake_user_image`` must also be set.
    Otherwise, these fields may be omitted.

    :ivar email: :class:`StringField` - The email address to be whitelisted
    :ivar name: :class:`StringField` - The name of the user to whitelist (fake
        users only)
    :ivar fake_user_image: :class:`StringField` - A URL to a profile picture
        (fake users only)
    :ivar user_type: :class:`RadioField` - The permission level for the user.
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
