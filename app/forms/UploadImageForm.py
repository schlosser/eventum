"""
.. module:: UploadImageForm
    :synopsis: A form to upload an :class:`~app.models.Image`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask.ext.wtf import Form
from wtforms import StringField, FileField
from wtforms.validators import Regexp, Required
from app.forms.validators import UniqueImage

class UploadImageForm(Form):
    """A form to upload an :class:`~app.models.Image`.

    :ivar image: :class:`FileField` - The image file that is being uploaded.
    :ivar uploaded_from: :class:`StringField` - A path to redirect to after
        uploading.
    :ivar filename: :class:`StringField` - The filename, without the extension.
    :ivar extension: :class:`StringField` - The filename extension, without
        the ``.``.
    """

    image = FileField('Image file')
    uploaded_from = StringField('Uploaded from')
    filename = StringField('Filename', [
        Regexp(r"([a-z]|[A-Z]|[0-9]|\||-|_|@|\(|\))*"),
        Required('Please submit a filename'),
        UniqueImage()])
    extension = StringField('Extension')
