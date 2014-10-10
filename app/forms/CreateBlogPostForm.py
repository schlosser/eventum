"""
.. module:: CreateBlogPostForm
    :synopsis: A form to create a `~app.models.BlogPost`.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from wtforms import FieldList, StringField, TextAreaField, BooleanField, SelectField
from flask.ext.wtf import Form
from wtforms.validators import Regexp, Required
from app.forms.validators import image_with_same_name

INVALID_SLUG = 'Post slug should only contain numbers, letters and dashes.'
BODY_DEFAULT = 'Type your post here.\n\nRendered in **Markdown**!'

class CreateBlogPostForm(Form):
    """A form for the creation of a :class:`~app.models.BlogPost` entry.

    The ``author`` field should be populated dynamically after the instance is
    created, using all of the :class:`~app.models.User` records as choices, and
    the current user as the default.

    :ivar title: :class:`wtforms.fields.StringField` - The title of the blog
        post.
    :ivar author: :class:`wtforms.fields.SelectField` - The author of the post.
        Populated dynamically.
    :ivar slug: :class:`wtforms.fields.StringField` - A unique url fragment for
        this blog post. This may only contain letters, numbers, and dashes
        (``-``).
    :ivar body: :class:`wtforms.fields.TextAreaField` - The markdown text for
        the body of the post.
    :ivar images: :class:`wtforms.fields.FieldList` of
        :class:`wtforms.fields.StringField` s - a list of image filenames that
        are used in the post body or as the featured image.
    :published: :class:`wtforms.fields.BooleanField` - Whether or not the post
        is published.
    :featured_image: :class:`wtforms.fields.StringField` - The filename of the
        featured image.
    """

    title = StringField('Title', [
        Required(message="Please provide the post title.")])
    author = SelectField('Author')

    # TODO: make slugs actually unique
    slug = StringField('Post Slug',
                       [Required(message="Please provide a post slug."),
                        Regexp('([0-9]|[a-z]|[A-Z]|-)*', message=INVALID_SLUG)])
    body = TextAreaField('Post Body',
                         [Required(message="Please provide a post body.")],
                         default=BODY_DEFAULT)
    images = FieldList(StringField('Image', [image_with_same_name]),
                       [Required("add images!")])
    published = BooleanField('Published')
    featured_image = StringField('Featured Image', [image_with_same_name])
