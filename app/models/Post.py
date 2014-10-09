from app import db
from app.models import User
from datetime import datetime
import markdown
now = datetime.now

class Post(db.Document):
    """A generic post object.
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
    images = db.ListField(
        db.ReferenceField('Image'))
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
        return str(self.id)

    def clean(self):
        """Update date_modified, and fill in posted_by and html_content
        if invalid
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
        return self.title

    def __repr__(self):
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
