"""
.. module:: BlogPost
    :synopsis: A blog post database model.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""
import re
from datetime import datetime

from common.interface import client_url_for
from eventum.models import Post
from eventum.lib.text import truncate_html

now = datetime.now

class BlogPost(Post):
    """An subclass of :class:`Post` that provides methods specific to blog
    posts.

    Note: all of the fields on :class:`BlogPost` are defined in :class:`Post`.
    """

    def snippet(self, length=100, truncate_text="...", newlines=True,
                tags=True, images=False):
        """Trim the blog post's HTML contnet into a snippet.

        :param int length: The number of words to truncate to.
        :param str truncate_text: The text to append to truncated text.
        :param bool newlines: Whether or not to preserve newlines.
        :param bool tags: Whether or not to trim HTML tags or not.
        :param bool images: Whether or not to trim images as well.

        :returns: The truncated text.
        :rtype: str
        """
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
        """Returns the absolute URL of this blog post.

        :returns: The url.
        :rtype: str
        """
        return client_url_for('blog.post', slug=self.slug)

    def human_readable_date(self):
        """Retuns the date this post was published, formatted like Oct 08, 2014.

        :returns: The formatted date
        :rtype: str
        """
        return self.date_published.strftime('%b %d, %Y')

    def pretty_date(self):
        """Returns the date publsihed or modified, to be used in the admin
        interface.

        :returns: The formatted date
        :rtype: str
        """
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
        """Returns the status of this post. Either ``'published'``,
        ``'complete'``, or ``'incomplete'``.

        :returns: The status
        :rtype: str
        """
        if self.published:
            return 'published'
        if self.html_content and self.title and self.slug and self.author:
            return 'complete'
        return 'incomplete'
