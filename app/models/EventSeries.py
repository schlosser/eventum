from mongoengine import ValidationError
from app.models.fields import DateField
from app import db
from datetime import datetime
now = datetime.now


class EventSeries(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=now)
    date_modified = db.DateTimeField(required=True, default=now)
    slug = db.StringField(required=True, max_length=255)
    events = db.ListField(db.ReferenceField("Event"))
    frequency = db.StringField(default="weekly")
    every = db.IntField(min_value=1, max_value=30)
    ends_after = db.BooleanField(default=True)
    ends_on = db.BooleanField(default=False)
    num_occurrences = db.IntField(default=1)
    recurrence_end_date = DateField()
    recurrence_summary = db.StringField()
    gcal_id = db.StringField() # ID of the first event in the series

    def delete_one(self, event):
        """"""
        self.events.remove(event)
        event.delete()
        self.save()

    def delete_all_except(self, event):
        """"""
        for e in self.events[:]:
            if e != event:
                e.delete()
        event.parent_series = None
        self.delete()

    def delete_all(self):
        """"""
        for e in self.events:
            e.delete()
        self.delete()

    def clean(self):
        """Update date_modified, and ensure that exactly one of `ends_after`
        and `ends_on` is True at a time.
        """
        self.date_modified = now()

        if self.ends_after == self.ends_on:
            raise ValidationError("ends_on and ends_after should not share a "
                                  "value.")

