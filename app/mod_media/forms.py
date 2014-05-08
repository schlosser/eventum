from flask.ext.wtf import Form
from wtforms import TextField, FileField
from wtforms.validators import Regexp, Required

class UploadImageForm(Form):
    image = FileField('Image file')
    filename = TextField('Filename', [
        Regexp("([a-z]|[A-Z]|[0-9]|\||-|_|@|\(|\))*"),
        Required('Please submit a filename')])
