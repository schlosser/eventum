"""
.. module:: validators
    :synopsis: Any validators for :mod:`wtforms` fields.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app.models import Image
from wtforms.validators import ValidationError
from app.models import Whitelist

def image_with_same_name(form, field):
    """A validator that ensures that there is an image in the database with the
    filename that is the same as the field's data.

    :param form: The parent form
    :type form: :class:`Form`
    :param field: The field to validate
    :type field: :class:`Field`
    """
    if Image.objects(filename=field.data).count() != 1:
        return ValidationError(
            message="Can't find image `%s` in the database" % field.data)


class UniqueEvent(object):
    """A validator that ensures that an event slug is unique.

    Checks the field data against the slugs in the :class:`Event` and
    :class:`EventSeries` collections, so that

        ``url_for('client.events', slug={{ some slug }})``

    is unique.
    """

    def __init__(self, message=None):
        """Ensures that slugs are unique in the :class:`Event` and
        :class:`EventSeries` collections.

        :param str message: An alternate message to be raised.
        """
        if not message:
            message = "An event with that slug already exists."
        self.message = message

    def __call__(self, form, field):
        """Called internally by :mod:`wtforms` on validation of the field.

        :param form: The parent form
        :type form: :class:`Form`
        :param field: The field to validate
        :type field: :class:`Field`
        :raises: :exc:`ValidationError`
        """
        from app.models import Event, EventSeries

        if EventSeries.objects(slug=field.data).count() != 0:
            raise ValidationError(self.message)
        if Event.objects(slug=field.data).count() != 0:
            raise ValidationError(self.message)


class UniqueImage(object):
    """A validator that verifies whether or not an image filename is unique in
    the :class:`Image` collection.
    """

    def __init__(self, message=None):
        """Ensures filenames are unique in the :class:`Image` collection.

        :param str message: An alternate message to be raised.
        """

        if not message:
            message = u'A image with that name already exists'
        self.message = message

    def __call__(self, form, field):
        """Called internally by :mod:`wtforms` on validation of the field.

        :param form: The parent form
        :type form: :class:`Form`
        :param field: The field to validate
        :type field: :class:`Field`
        :raises: :exc:`ValidationError`
        """

        filename = '%s.' % field.data
        if Image.objects(filename__startswith=filename).count() != 0:
            raise ValidationError(self.message)


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
