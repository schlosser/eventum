from datetime import datetime
now = datetime.now
class DBItem():

    def __init__(self, person=None):
        self._id = None
        self.date_created = now()
        self.date_modified = now()

    def __repr__(self):
        return 'DBItem(_id=%r, date_created=%r, date_modified=%r)' % \
            (self._id, self.date_created, self.date_modified)


class Post(DBItem):

    def __init__(
        self, title, author, content, url_name, categories=[], tags=[],
            published=False, date_published=None, posted_by=None):
        """Create a new Post instance

        Arguments:
        title -- display title for the post
        author -- the Person that authored the post
        content -- the HTML body of the post
        url_name -- for use in the url (ie. my-cool-post)

        Keyword Arguments:
        tags -- list of tags (default: [])
        categories -- list of categories (default: [])
        published -- is the post published? (default: False)
        date_published -- date the post is published (default: None)
        posted_by -- Person who posted, if different from author (default: None)
        """
        super(Post, self).__init__()

        self.title = title
        self.author = author
        self.content = content
        self.categories = categories
        self.tags = tags
        self.published = published
        self.date_published = date_published
        self.posted_by = posted_by if posted_by else author

    def __repr__(self):
        rep = '%r(title=%r, author=%r, categories=%r, tags=%r, published=%r' %\
            (self.__class__.__name__, self.title, self.author, self.categories,
             self.tags, self.published)

        # excluded if None
        rep += ', date_published=%r' % (self.date_published) \
            if self.date_published else ""
        rep += ', posted_by=%r' % (self.posted_by) if self.posted_by else ""

        # cut down to 100 characters
        if len(self.content) > 100:
            rep += ', content=%r' % (self.content[:97] + "...")
        else:
            rep += ', content=%r' % (self.content)
        return rep
