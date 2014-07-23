from flask.ext.wtf import Form
from wtforms import TextField, FileField
from wtforms.validators import Regexp, Required, ValidationError
from app.models import Image

class Unique(object):
    def __init__(self, message=None):
        if not message:
            message = u'A image with that name already exists'
        self.message = message

    def __call__(self, form, field):
        filename = '%s.' % field.data
        if Image.objects(filename__startswith=filename).count() != 0:
            raise ValidationError(self.message)

class UploadImageForm(Form):
    image = FileField('Image file')
    uploaded_from = TextField('Uploaded from')
    filename = TextField('Filename', [
        Regexp("([a-z]|[A-Z]|[0-9]|\||-|_|@|\(|\))*"),
        Required('Please submit a filename'),
        Unique()])
    extension = TextField('Extension')
