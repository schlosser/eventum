import re
from datetime import datetime

from flask import url_for

from app.models import Post
from app.lib.text import truncate_html

now = datetime.now

class BlogPost(Post):
    """"""

    def snippet(self, length=100, truncate_text="...", newlines=True,
                tags=True, images=False):
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

    def human_readable_date(self):
        return self.date_published.strftime('%b %d, %Y')

    def pretty_date(self):
        if self.published:
            return self.date_published.strftime("Published %d/%b/%y")
        return self.date_modified.strftime("Modified %d/%b/%y")

    def publish(self):
        self.published = True
        self.date_published = now()
        self.save()
    def unpublish(self):
        self.published = False
        self.date_published = None
        self.save()

    def status(self):
        if self.published:
            return 'published'
        if self.html_content and self.title and self.slug and self.author:
            return 'complete'
        return 'incomplete'

