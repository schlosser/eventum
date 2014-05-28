from mongoengine import ValidationError
from app.auth.models import User
from app.events.fields import DateField, TimeField
from app import db
from datetime import datetime
now = datetime.now


class EventSeries(db.Document):
    """"""
    pass


class Event(db.Document):
    """"""
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
    event_series = db.ListField(
        db.ReferenceField(
            "Event", verbose_name="Event in Series",
            help_text="Another event in the same series as this event."
        ), verbose_name="Events Series",
        help_text="A list of the other events in the series if this is a "
        "recurring event.")
    root_event = db.ReferenceField("Event", verbose_name="Parent Event",
        help_text="The first event in this series of reocurring events.")
    repeat = db.BooleanField(verbose_name="Repeat",
        help_text="Whether this event is recurring or not.")
    frequency = db.StringField(default="weekly",
        verbose_name="Repeat Frequency",
        help_text="The frequency with which the repeats")
    every = db.IntField(verbose_name="Every", min_value=1, max_value=30,
        help_text="Number of frequency units between events (i.e. 3 = every"
            " three weeks")
    ends = db.StringField(regex="(on|after)", verbose_name="Ends",
        help_text="Whether or not the event ends on a certain date or after a "
        "certain number of occurances.")
    num_occurances = db.IntField(default=1, verbose_name="Number of Occurances",
        help_text="Number of times that the event repeats (if ends='after')")
    repeat_end_date = DateField(verbose_name="Repeat End Date",
        help_text="The date after which the event will stop happening.")
    summary = db.StringField(verbose_name="Repeat Configuration Summary",
        help_text="A human-readable summary of how the event is configured to "
        "repeat")


    def clean(self):
        """Update date_modified, and validate datetimes to ensure the event ends
        after it starts.
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

    def id_str(self):
        return str(self.id)

    def ready_for_publishing(self):
        """"""
        return all([
            self.title,
            self.creator,
            self.location,
            self.start_datetime(),
            self.end_datetime(),
            self.descriptions.get('short'),
            self.descriptions.get('long')
            ])

    def human_readable_datetime(self):
        """Format the start and end date date in one of the following three
        formats:
            1. Sun, 3/31 11:00 PM - Mon, 4/1 3:00 AM
            2. Sun, 3/31 11:00 AM - 2:00 PM
            3. Sun, 3/31 3:00 - 7:30 PM
        Depending on whether or not the start / end times / dates are the same.
        All unkown values will be replaced by question marks.
        """
        output = ""
        if self.start_date:
            output += self.start_date.strftime("%a, %m/%d ") \
                .replace(" 0", " ").replace("/0", "/")
        else:
            output += "???, ??/?? "
        if self.start_time:
            start_format = "%I:%M - " if self.end_time and \
                self.start_time.strftime("%p")==self.end_time.strftime("%p") \
                else "%I:%M %p - "
            output += self.start_time.strftime(start_format).lstrip("0")
        else:
            output += "??:?? - "
        if self.end_date:
            if self.start_date and self.start_date != self.end_date:
                output += self.end_date.strftime("%a, %m/%d ") \
                    .replace(" 0", " ").replace("/0", "/")
        else:
            output += "???, ??/?? "
        if self.end_time:
            output += self.end_time.strftime("%I:%M %p").lstrip("0")
        else:
            output += "??:??"
        return output

    meta = {
        'allow_inheritance': True,
        'indexes': ['start_date', 'creator'],
        'ordering': ['-start_date']
    }

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return 'Event(title=%r, location=%r, creator=%r, start=%r, end=%r, ' \
            'published=%r' % (self.title, self.location, self.creator,
                             self.start_datetime(), self.end_datetime(),
                             self.published)
