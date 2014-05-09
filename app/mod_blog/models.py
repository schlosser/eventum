from app.mod_base.models import Post
from app.mod_media.models import Image
from app.mod_blog.utils import truncate_html
from flask import url_for
from app import db

class BlogPost(Post):

    images = db.ListField(
        db.ReferenceField(Image, verbose_name="Image",
            help_text="An image that is associated with the blog post."),
        verbose_name="Associated Images",
        help_text="A list of all of the images in this blog post")

    def snippet(self, length=100, truncate_text="..."):
        return truncate_html(self.html_content, length, truncate_text)

    def get_absolute_url(self):
        return url_for('blog.post', slug=self.slug)
