from mongoengine import ValidationError
from app.mod_auth.models import User
from app import db
from datetime import datetime
now = datetime.now

class Event(db.Document):

    date_created = db.DateTimeField(
        default=now, required=True,verbose_name="Date Created",
        help_text="DateTime when the document was created, localized to the server")
    date_modified = db.DateTimeField(
        default=now, required=True, verbose_name="Date Modified",
        help_text="DateTime when the document was last modified, localized to the server")
    title = db.StringField(
        max_length=255, required=True, verbose_name="Title",
        help_text="Title of the event (255 characters max)")
    location = db.StringField(
        verbose_name="Location", help_text="The location of the event")
    owner = db.ReferenceField(
        User, required=True, verbose_name="Owner",
        help_text="Reference to the User that is in charge of the event")
    start_date = db.DateTimeField(
        required=True, verbose_name="Start Date",
        help_text="Start date of the event, localized to the server")
    end_date = db.DateTimeField(
        required=True, verbose_name="End Date",
        help_text="End date of the event, localized to the server")
    descriptions = db.DictField(
        required=True, verbose_name="Descriptions", default={
            "short": None,
            "long": None
        }, help_text="A dictionary of descriptons with their types as keys")
    published = db.BooleanField(
        required=True, default=False, verbose_name="Published",
        help_text="Whether or not the post is published")
    date_published = db.DateTimeField(
        verbose_name="Date Published",
        help_text="The date when the post is published, localized to the server")

    def clean(self) :
        """Update date_modified, and ensure that end_date is after start_date.

        If end_date is before start_date, throw ValueError
        """
        self.date_modified = now()
        if self.start_date > self.end_date:
            raise ValidationError("Start date should always come before end date",
                                  self.start_date, self.end_date)

    meta = {
        'allow_inheritance': True,
        'indexes': ['start_date', 'owner'],
        'ordering': ['-start_date']
    }

    def __unicode__(self):
        return self.title

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

