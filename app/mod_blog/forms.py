from flask.ext.wtf import Form
from wtforms import TextAreaField, TextField
from wtforms.validators import Required, Regexp

class CreateBlogPostForm(Form):

    title = TextField('Title', [
        Required(message="Please provide the post title.")])
    slug = TextField('Post Slug', [
        Required(message="Please provide a post slug."),
        Regexp('([0-9]|[a-z]|[A-Z]|-)*', message="Post slug should only contain numbers, letters and dashes.")])
    body = TextAreaField('Post Body', [
        Required(message="Please provide a post body.")])
