"""
.. module:: Post
    :synopsis: A generic post database model.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from app import db
from app.models import User
from datetime import datetime
import markdown
now = datetime.now

class Post(db.Document):
    """A generic post object.

    :ivar date_created: :class:`mongoengine.DateTimeField` - The date the post
        was created.
    :ivar date_modified: :class:`mongoengine.DateTimeField` - The date the post
        was last modified.
    :ivar title: :class:`mongoengine.StringField` - The title of the post.
    :ivar author: :class:`mongoengine.ReferenceField` - The author of the post.
    :ivar html_content: :class:`mongoengine.StringField` - The HTML body of the
        post.
    :ivar markdown_content: :class:`mongoengine.StringField` - The markdown
        body of the post, which will be rendered to HTML.
    :ivar images: :class:`mongoengine.ListField` of
        :class:`mongoengine.ReferenceField` - The images for this blog post.
    :ivar featured_image: :class:`mongoengine.ReferenceField` - The featured
        image on this post.
    :ivar slug: :class:`mongoengine.StringField` - The URL slug associated with
        this post.
    :ivar categories: :class:`mongoengine.ListField` of
        :class:`mongoengine.StringField` - A list of categories for this post.
    :ivar tags: :class:`mongoengine.ListField` of
        :class:`mongoengine.StringField` - A list of tags for this post.
    :ivar published: :class:`mongoengine.BooleanField` - True if the event is
        published.
    :ivar date_published: :class:`mongoengine.DateTimeField` - The date when
        this post was published.
    :ivar posted_by: :class:`mongoengine.ReferenceField` - The user that posted
        this event. This may be different than the post's author, if the author
        was a guest writer or someone not registered with Eventum.
    """

    # MongoEngine ORM metadata
    meta = {
        'allow_inheritance': True,
        'indexes': ['title', 'date_created'],
        'ordering': ['-date_created']
    }

    date_created = db.DateTimeField(required=True, default=now)
    date_modified = db.DateTimeField(required=True, default=now)
    title = db.StringField(required=True, max_length=255)
    author = db.ReferenceField(User, required=True)
    html_content = db.StringField()
    markdown_content = db.StringField(required=True)
    images = db.ListField(db.ReferenceField('Image'))
    featured_image = db.ReferenceField('Image')
    slug = db.StringField(required=True, regex="([a-z]|[A-Z]|[1-9]|-)*")
    categories = db.ListField(db.StringField(db_field='category',
                                             max_length=255),
                              default=list)
    tags = db.ListField(db.StringField(db_field='tag', max_length=255),
                        default=list)
    published = db.BooleanField(required=True, default=False)
    date_published = db.DateTimeField()
    posted_by = db.ReferenceField(User, required=True)

    def id_str(self):
        """The id of this object, as a string.

        :returns: The id
        :rtype: str
        """
        return str(self.id)

    def clean(self):
        """Called by Mongoengine on every ``.save()`` to the object.

        Update date_modified, and fill in posted_by and html_content
        if invalid.

        :raises: :class:`ValidationError`
        """

        self.date_modified = now()

        self.html_content = markdown.markdown(self.markdown_content,
                                              ['extra', 'smarty'])
        if self.images:
            for image in self.images:
                self.html_content = self.html_content.replace(
                    'src="' + image.filename + '"',
                    'src="' + image.url() + '"')
        if not self.posted_by:
            self.posted_by = self.author
        if self.published and not self.date_published:
            self.date_published = now()

    def __unicode__(self):
        """This post, as a unicode string.

        :returns: The title of the post
        :rtype: str
        """
        return self.title

    def __repr__(self):
        """The representation of this post.

        :returns: The post's details.
        :rtype: str
        """
        rep = '%r(title=%r, author=%r, categories=%r, tags=%r, published=%r' %\
            (self.__class__.__name__, self.title, self.author, self.categories,
             self.tags, self.published)

        # excluded if None
        rep += ', date_published=%r' % (self.date_published) \
            if self.date_published else ""
        rep += ', posted_by=%r' % (self.posted_by) if self.posted_by else ""

        # cut down to 100 characters
        if len(self.html_content) > 100:
            rep += ', html_content=%r' % (self.html_content[:97] + "...")
        else:
            rep += ', html_content=%r' % (self.html_content)
        return rep
