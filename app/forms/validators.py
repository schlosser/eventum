from app.models import Image
from wtforms.validators import ValidationError

def image_with_same_name(form,field):
    if Image.objects(filename=field.data).count() != 1:
        return ValidationError(
            message="Can't find image `%s` in the database" % field.data)