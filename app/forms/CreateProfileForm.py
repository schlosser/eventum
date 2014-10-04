"""
.. module:: CreateProfileForm
    :synopsis: A form for completing a user's profile.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask.ext.wtf import Form
from wtforms import StringField, HiddenField
from wtforms.validators import URL, Email, Required

EMAIL_ERROR = 'Please provide a valid email address.'

class CreateProfileForm(Form):
    """A form for completing a :class:`~app.models.User` profile after they
    login to Eventum for the first time.

    :ivar email: :class:`StringField` - The user's email address.
    :ivar name: :class:`StringField` - The user's name.
    :ivar next: :class:`HiddenField` - The URL that they should be redirected
        to after completing their profile.
    """
    name = StringField('Full Name')
    email = StringField('Email Address',[Email(message=EMAIL_ERROR),
                                         Required(message=EMAIL_ERROR)])
    next = HiddenField('hidden', [URL(require_tld=False)])