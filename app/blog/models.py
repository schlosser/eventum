from app.base.models import Post
from app.media.models import Image
from app.blog.utils import truncate_html
from flask import url_for
from app import db
import re

class BlogPost(Post):

    images = db.ListField(
        db.ReferenceField(Image, verbose_name="Image",
            help_text="An image that is associated with the blog post."),
        verbose_name="Associated Images",
        help_text="A list of all of the images in this blog post")

    def snippet(self, length=100, truncate_text="...", newlines=True, tags=True, images=False):
        html = truncate_html(self.html_content, length, truncate_text)
        if not newlines:
            html = html.replace('\n', ' ')
        if not tags:
            p = re.compile(r'<.*?>')
            html = p.sub(' ', html)
        if not images:
            p = re.compile(r'<img.*?/>')
            html = p.sub(' ', html)
        return html

    def get_absolute_url(self):
        return url_for('blog.post', slug=self.slug)

    def pretty_date(self):
        if self.published:
            return self.date_published.strftime("Published %d/%b/%y")
        return self.date_modified.strftime("Modified %d/%b/%y")

