from wtforms import FieldList, StringField, TextAreaField, BooleanField, SelectField
from flask.ext.wtf import Form
from wtforms.validators import Regexp, Required
from app.forms.validators import image_with_same_name

class CreateBlogPostForm(Form):

    title = StringField('Title', [
        Required(message="Please provide the post title.")])
    author = SelectField('Author')
    slug = StringField('Post Slug', [
        Required(message="Please provide a post slug."),
        Regexp('([0-9]|[a-z]|[A-Z]|-)*', message="Post slug should only contain numbers, letters and dashes.")])
    body = TextAreaField('Post Body', [
        Required(message="Please provide a post body.")],
        default="Type your post here.\n\nRendered in **Markdown**!")
    images = FieldList(StringField('Image', [image_with_same_name]), [Required("add images!")])
    published = BooleanField('Published')
    featured_image = StringField('Featured Image', [image_with_same_name])
