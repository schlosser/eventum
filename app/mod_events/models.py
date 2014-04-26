from mongoengine import ValidationError
from mongoengine.base import BaseField
from mongoengine.fields import DateTimeField
from app.mod_auth.models import User
from app import db
from datetime import datetime, time, date
now = datetime.now


class TimeField(BaseField):

    """A datetime.time field.

    Looks to the outside world like a datatime.time, but stores in the
    database as an int/float number of seconds since midnight.
    """

    def validate(self, value):
        """Only accepts a datetime.time, or a int/float number of seconds
        since midnight.
        """
        if not isinstance(value, (time, int, float)):
            self.error(u'cannot parse time "%r"' % value)

    def to_mongo(self, value):
        """Wrapper on top of prepare_query_value"""
        return self.prepare_query_value(None, value)

    def to_python(self, value):
        """Convert the int/float number of seconds since midnight to a
        time"""
        if isinstance(value, (int, float)):
            value = int(value)
            return time(hour=value/3600, minute=value%3600/60, second=value%60)
        return value

    def prepare_query_value(self, op, value):
        """Convert from datetime.time to int/float number of seconds."""
        print "prepare_query_value %r" % value
        if value is None:
            return value
        if isinstance(value, time):
            return value.hour * 3600 + \
                   value.minute * 60 + \
                   value.second + \
                   value.microsecond / 1000000
        if isinstance(value, (int, float)):
            return value


class DateField(DateTimeField):

    """A datetime.date field.

    Looks to the outside world like a datatime.date, but functions
    as a datetime.datetime object in the database.s
    """

    def to_python(self, value):
        """Convert from datetime.datetime to datetime.date."""
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        raise ValueError("Unkown type '%r' of variable %r",type(value), value)


class Event(db.Document):

    date_created = db.DateTimeField(
        default=now, required=True, verbose_name="Date Created",
        help_text="DateTime when the document was created, localized to the server")
    date_modified = db.DateTimeField(
        default=now, required=True, verbose_name="Date Modified",
        help_text="DateTime when the document was last modified, localized to the server")
    title = db.StringField(
        max_length=255, required=True, verbose_name="Title",
        help_text="Title of the event (255 characters max)")
    location = db.StringField(
        verbose_name="Location", help_text="The location of the event")
    creator = db.ReferenceField(
        User, required=True, verbose_name="Owner",
        help_text="Reference to the User that is in charge of the event")
    start_date = DateField(
        verbose_name="Start Date",
        help_text="The date that the event starts")
    end_time = TimeField(
        verbose_name="End Time",
        help_text="The time of day that the event ends")
    end_date = DateField(
        verbose_name="End Date",
        help_text="The date that the event ends")
    start_time = TimeField(
        verbose_name="Start Time",
        help_text="The time of day that the event starts")
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

    def clean(self):
        """Update date_modified, and validate datetimes to ensure the event ends after
        it starts.
        """
        self.date_modified = now()

        if self.start_date and self.end_date and \
                self.start_date > self.end_date:
            raise ValidationError("Start date should always come before end "
                                  "date. Got (%r,%r)" % (self.start_date,
                                                         self.end_date))
        if self.start_time and self.end_time and \
                self.start_time > self.end_time:
            raise ValidationError("Start time should always come before end "
                                  "time. Got (%r,%r)" % (self.start_time,
                                                         self.end_time))

    def start_datetime(self):
        """A convenience method to combine start_date and start_time"""
        if self.start_date is None or self.start_time is None:
            return None
        return datetime.combine(self.start_date, self.start_time)

    def end_datetime(self):
        """A convenience method to combine end_date and end_time"""
        if self.end_date is None or self.end_time is None:
            return None
        return datetime.combine(self.end_date, self.end_time)

    def ready_for_publishing(self):
        return all([
            self.title,
            self.creator,
            self.location,
            self.start_datetime(),
            self.end_datetime(),
            self.descriptions.short,
            self.descriptions.long
            ])


    meta = {
        'allow_inheritance': True,
        'indexes': ['start_date', 'creator'],
        'ordering': ['-start_date']
    }

    def __unicode__(self):
        return self.title

    def __repr__(self):
        rep = 'Event(title=%r, location=%r, creator=%r, start=%r, end=%r, \
            published=%r' % (self.title, self.location, self.creator, self.start_datetime(),
                             self.end_datetime(), self.published)
        rep += ', short_description=%r' % \
            self.descriptions['short'] if self.descriptions['short'] else ""
        rep += ', long_description=%r' % \
            self.descriptions['long'] if self.descriptions['long'] else ""
        rep += ', date_published=%r' % (self.date_published) if self.date_published else ""
        return rep
