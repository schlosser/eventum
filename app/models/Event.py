from mongoengine import ValidationError
from app import db
from app.forms.fields import DateField
from app.models.fields import TimeField

from datetime import datetime
now = datetime.now

class Event(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=now)
    date_modified = db.DateTimeField(required=True, default=now)
    title = db.StringField(required=True, max_length=255)
    creator = db.ReferenceField("User", required=True)
    location = db.StringField()
    start_date = DateField()
    end_time = TimeField()
    end_date = DateField()
    start_time = TimeField()
    short_description = db.StringField()
    long_description = db.StringField()
    is_published = db.BooleanField(required=True, default=False)
    date_published = db.DateTimeField()
    is_recurring = db.BooleanField(required=True, default=False)
    parent_series = db.ReferenceField("EventSeries")
    image = db.ReferenceField("Image")
    gcal_id = db.StringField()
    gcal_calendar_id = db.StringField()

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
            self.short_description,
            self.long_description,
            self.image
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
            'is_published=%r' % (self.title, self.location, self.creator,
                             self.start_datetime(), self.end_datetime(),
                             self.is_published)
