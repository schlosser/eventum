from app.mod_base.models import DBItem

class Event(DBItem):

    def __init__(self, title, location, start_date, end_date,
                 published=False, short_description="", long_description="",
                 date_published=None, posted_by=None):
        self.title = title
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.short_description = short_description
        self.long_description = long_description
        self.published = published
        self.date_published = date_published
        self.posted_by = posted_by if posted_by else self.author

    def __repr__(self):
        rep = 'Event(title=%r, location=%r, start_date=%r, end_date=%r, \
            published=%r' % (self.title, self.location, self.start_date,
                             self.end_date, self.published)
        rep += ', short_description=%r' % \
            self.short_description if self.short_description else ""
        rep += ', long_description=%r' % \
            self.long_description if self.long_description else ""
        rep += ', date_published=%r' % (self.date_published) if self.date_published else ""
        rep += ', posted_by=%r' % (self.posted_by) if self.posted_by else ""
        return rep

