"""
.. module:: Whitelist
    :synopsis: A database model to store a whitelisted user.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from datetime import datetime
from mongoengine import (Document, DateTimeField, EmailField, StringField,
                         BooleanField)
from eventum.models.User import USER_TYPE_REGEX
from eventum.models import BaseEventumDocument

now = datetime.now


class Whitelist(Document, BaseEventumDocument):
    """A database model to hold an entry on the Whitelist.

    Only users that are on the Whitelist may make accounts with Eventum. Once
    they authenticate with the whitelisted email, a :class:`~app.models.User`
    object is made, but the whitelist entry remains, but is marked redeemed.

    :ivar date_created: :class:`mongoengine.fields.DateTimeField` - The date
        that the whitelist entry was created.
    :ivar date_modified: :class:`mongoengine.fields.DateTimeField` - The date
        when the whitelist entry was last modified.
    :ivar email: :class:`mongoengine.fields.EmailField` - The email to be
        whitelisted.
    :ivar user_type: :class:`mongoengine.fields.StringField` - The user type to
        associate with the email address.
    :ivar redeemed: :class:`mongoengine.fields.BooleanField` - True if the user
        has authenticated with this email and made an account on Eventum.
    """
    date_created = DateTimeField(required=True, default=now)
    date_modified = DateTimeField(required=True, default=now)
    email = EmailField(required=True, unique=True)
    user_type = StringField(default='editor', regex=USER_TYPE_REGEX)
    redeemed = BooleanField(required=True, default=False)

    # MongoEngine ORM metadata
    meta = {'indexes': ['email']}

    def clean(self):
        """Called by Mongoengine on every ``.save()`` to the object.

        Updates ``date_modified``.
        """
        self.date_modified = now()

    def __repr__(self):
        """The representation of this Whitelist entry.

        :returns: The entry's details.
        :rtype: str
        """
        return 'Whitelist(email={}, user_type={}, redeemed={})'.fomrat(
            self.email,
            self.user_type,
            self.redeemed
        )

    def __unicode__(self):
        """This Whitelist entry, as a unicode string.

        :returns: The whitelisted email
        :rtype: str
        """
        return 'Whitelist<%r>' % self.email
