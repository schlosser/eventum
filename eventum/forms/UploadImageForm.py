"""
.. module:: UploadImageForm
    :synopsis: A form to upload an :class:`~app.models.Image`.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from flask.ext.wtf import Form
from wtforms import StringField, FileField
from wtforms.validators import Regexp, Required
from eventum.forms.validators import UniqueImage
from eventum.lib.regex import Regex


class UploadImageForm(Form):
    """A form to upload an :class:`~app.models.Image`.

    :ivar image: :class:`wtforms.fields.FileField` - The image file that is
        being uploaded.
    :ivar uploaded_from: :class:`wtforms.fields.StringField` - A path to
        redirect to after uploading.
    :ivar filename: :class:`wtforms.fields.StringField` - The filename, without
        the extension.
    :ivar extension: :class:`wtforms.fields.StringField` - The filename
        extension, without the ``.``.
    """

    image = FileField('Image file')
    uploaded_from = StringField('Uploaded from')
    filename = StringField('Filename', [
        Regexp(Regex.FILENAME_REGEX,
               message='Your filename should only contain uppercase and '
                       'lowercase letters, numbers, and underscores.'),
        Required('Please submit a filename.'),
        UniqueImage()])
    extension = StringField('Extension', [
        Regexp(Regex.EXTENSION_REGEX,
               message='Only .png, .jpg, .jpeg, and .gif files are allowed.'),
        Required('Please ensure your file has an extension.')])
