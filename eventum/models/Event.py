"""
.. module:: Event
    :synopsis: An event database model.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask import url_for
from mongoengine import ValidationError
from eventum import app, db
from eventum.models.fields import DateField, TimeField
import markdown

from datetime import datetime, timedelta
now = datetime.now

class Event(db.Document):
    """The object that represents an individual event in Mongoengine.

    Recurring events also have a :class:`~app.models.EventSeries` instance that
    connects them to the other events in the series.

    :ivar date_created: :class:`mongoengine.fields.DateTimeField` - The date
        that the event object was created.
    :ivar date_modified: :class:`mongoengine.fields.DateTimeField` - The last
        date the event was modified.
    :ivar title: :class:`mongoengine.fields.StringField` - The title of the
        event.
    :ivar creator: :class:`mongoengine.fields.ReferenceField` - The User that
        created the event.
    :ivar location: :class:`mongoengine.fields.StringField` - The event's
        location.
    :ivar slug: :class:`mongoengine.fields.StringField` - The URL slug
        associated with the event. **Note:** appending the slug to the base
        path for events will not always yield the functioning URL for the
        event, because recurring events have indexes appended to the url. User
        :func:`get_absolute_url` always.
    :ivar start_date: :class:`DateField` - The date the event starts.
    :ivar end_date: :class:`DateField` - The date the event ends
    :ivar start_time: :class:`TimeField` - The time the event starts
    :ivar end_time: :class:`TimeField` - The time the event ends
    :ivar short_description: :class:`mongoengine.fields.StringField` - The HTML
        short description of the event.
    :ivar long_description: :class:`mongoengine.fields.StringField` - The HTML
        long description of the event.
    :ivar short_description_markdown: :class:`mongoengine.fields.StringField` -
        The markdown short description of the event.
    :ivar long_description_markdown: :class:`mongoengine.fields.StringField` -
        The markdown long description of the event.
    :ivar published: :class:`mongoengine.fields.BooleanField` - True if the
        event is published.
    :ivar date_published: :class:`mongoengine.fields.DateTimeField` - The date
        that the event was published.
    :ivar is_recurring: :class:`mongoengine.fields.BooleanField` - True if the
        event is recurring.
    :ivar parent_series: :class:`mongoengine.fields.ReferenceField` - The
        :class:`~app.models.EventSeries` object that holds the recurrence info
        for an event, if it is recurring.
    :ivar image: :class:`mongoengine.fields.ReferenceField` - The headline
        image for the event.
    :ivar facebook_url: :class:`mongoengine.fields.StringField` - The URL to
        the Facebook event associated with this event.
    :ivar gcal_id: :class:`mongoengine.fields.StringField` - The ID for this
        event on Google Calendar. In Google Calendar API responses, this is
        stored asthe ``id`` field for events. If this field is None, then we
        never got a proper response from Google Calendar when (if) we made a
        request to create it there. It most likely does not exist on Google
        Calendar.
    :ivar gcal_sequence: :class:`mongoengine.fields.IntField` - The sequence
        number for the event, used by Google Calendar for versioning.
    """

    # MongoEngine ORM metadata
    meta = {
        'allow_inheritance': True,
        'indexes': ['start_date', 'creator'],
        'ordering': ['-start_date']
    }

    date_created = db.DateTimeField(required=True, default=now)
    date_modified = db.DateTimeField(required=True, default=now)
    title = db.StringField(required=True, max_length=255)
    creator = db.ReferenceField("User", required=True)
    location = db.StringField()
    slug = db.StringField(required=True, max_length=255)
    start_date = DateField()
    end_date = DateField()
    start_time = TimeField()
    end_time = TimeField()
    short_description = db.StringField()
    long_description = db.StringField()
    short_description_markdown = db.StringField()
    long_description_markdown = db.StringField()
    published = db.BooleanField(required=True, default=False)
    date_published = db.DateTimeField()
    is_recurring = db.BooleanField(required=True, default=False)
    parent_series = db.ReferenceField("EventSeries")
    image = db.ReferenceField("Image")
    facebook_url = db.StringField()
    gcal_id = db.StringField()
    gcal_sequence = db.IntField()

    def get_absolute_url(self):
        """Returns the URL path that points to the client-facing version of
        this event.

        :returns: A URL path like ``"/events/cookies-and-code"``.
        :rtype: str
        """
        if self.is_recurring:
            return url_for('home.recurring_event', slug=self.slug, index=self.index)
        return url_for('home.event', slug=self.slug)

    def image_url(self):
        """Returns the URL path that points to the image for the event.

        :returns: The URL path like ``"/static/img/cat.jpg"``.
        :rtype: str
        """
        if self.image:
            return self.image.url()
        return url_for('static', filename=app.config['DEFAULT_EVENT_IMAGE'])

    @property
    def index(self):
        """Represents the index of this event in it's parent
        :class:`~app.models.EventSeries`. Returns ``None`` if the event is not
        recurring.

        :returns: The index of the event in it's series.
        :rtype: int
        """
        if not self.is_recurring:
            return
        return self.parent_series.events.index(self)

    def clean(self):
        """Called by Mongoengine on every ``.save()`` to the object.

        Updates date_modified, renders the markdown into the HTML fields, and
        validates datetimes to ensure the event ends after it starts.

        :raises: :class:`wtforms.validators.ValidationError`
        """
        self.date_modified = now()

        if self.short_description_markdown:
            self.short_description = markdown.markdown(self.short_description_markdown,
                                                       ['extra', 'smarty'])

        if self.long_description_markdown:
            self.long_description = markdown.markdown(self.long_description_markdown,
                                                      ['extra', 'smarty'])

        if (self.start_date and
                self.end_date and
                self.start_date > self.end_date):
            raise ValidationError("Start date should always come before end "
                                  "date. Got (%r,%r)" % (self.start_date,
                                                         self.end_date))
        # Check times against None, because midnight is represented by 0.
        if (self.start_date == self.start_time and
                self.start_time is not None and
                self.end_time is not None and
                self.start_time > self.end_time):
            raise ValidationError("Start time should always come before end "
                                  "time. Got (%r,%r)" % (self.start_time,
                                                         self.end_time))

    def start_datetime(self):
        """A convenience method to combine ``start_date`` and ``start_time``
        into one :class:`datetime`.

        :returns: The combined datetime, or ``None` if ``start_date`` or
            ``start_time`` are ``None``.
        :rtype: :class:`datetime`.
        """
        # Check times against None, because midnight is represented by 0.
        if self.start_date is None or self.start_time is None:
            return None
        return datetime.combine(self.start_date, self.start_time)

    def end_datetime(self):
        """A convenience method to combine ``end_date`` and ``end_time``
        into one :class:`datetime`.

        :returns: The combined datetime, or ``None` if ``end_date`` or
            ``end_time`` are ``None``.
        :rtype: :class:`datetime`.
        """
        # Check times against None, because midnight is represented by 0.
        if self.end_date is None or self.end_time is None:
            return None
        return datetime.combine(self.end_date, self.end_time)

    def id_str(self):
        """The id of this object, as a string.

        :returns: The id
        :rtype: str
        """
        return str(self.id)

    def ready_for_publishing(self):
        """Returns True if the event has all necessary fields filled out.

        Necessary fields are:

        - ``title``
        - ``creator``
        - ``location``
        - ``start_datetime``
        - ``end_datetime``
        - ``short_description``
        - ``long_description``
        - ``image``

        :Returns: True if we are ready for publishing.
        :rtype: bool
        """
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

    def is_multiday(self):
        """Retuns True if the event spans muliple days.

        :returns: True if the event spans multiple days.
        :rtype: bool
        """
        if self.start_date == self.end_date:
            return False
        if self.start_date == self.end_date - timedelta(days=1) and self.end_time.hour < 5:
            return False
        return True

    def human_readable_date(self):
        """Return the date of the event (presumed not multiday) formatted like:
        ``"Sunday, Mar 31"``.

        :returns: The formatted date.
        :rtype: str
        """
        return self.start_date.strftime("%A, %b %d")

    def human_readable_time(self):
        """Return the time range of the event (presumed not multiday) formatted
        like ``"11am - 2:15pm"`` or ``"3 - 7:30pm"``.

        :returns: The formatted date.
        :rtype: str
        """
        output = ''
        if self.start_time.strftime("%p") == self.end_time.strftime("%p"):
            format = "%I:%M-"
        else:
            format = "%I:%M%p-"
        output += self.start_time.strftime(format).lstrip("0").lower()
        output += self.end_time.strftime("%I:%M%p").lower().lstrip("0")
        return output

    def human_readable_datetime(self):
        """Format the start and end date date in one of the following three
        formats:

        1. ``"Sunday, March 31 11pm - Monday, April 1 3am"``
        2. ``"Sunday, March 31 11am - 2:15pm"``
        3. ``"Sunday, March 31 3 - 7:30pm"``

        Depending on whether or not the start / end times / dates are the same.
        All unkown values will be replaced by question marks.

        :returns: The formatted date.
        :rtype: str
        """
        output = ""
        if self.start_date:
            output += self.start_date.strftime("%A, %B %d ") \
                .replace(" 0", " ").replace("/0", "/")
        else:
            output += "???, ??/?? "

        # Check times against None, because midnight is represented by 0.
        if self.start_time is not None:
            if self._start_and_end_time_share_am_or_pm():
                start_format = "%I:%M-"
            else:
                start_format = "%I:%M%p-"
            output += self.start_time.strftime(start_format).lstrip("0").lower()
        else:
            output += "??:?? - "

        if self.end_date:
            if self.start_date and self.start_date != self.end_date:
                output += self.end_date.strftime("%A, %B %d ") \
                    .replace(" 0", " ").replace("/0", "/")
        else:
            output += "???, ??/?? "

        # Check times against None, because midnight is represented by 0.
        if self.end_time is not None:
            output += self.end_time.strftime("%I:%M%p").lower().lstrip("0")
        else:
            output += "??:??"
        return output

    def _start_and_end_time_share_am_or_pm(self):
        """Returns True if the start and end times for an event are both pm or
        am.

        :returns: True if the start and end times for an event are both pm or
            am.
        :rtype: bool
        """
        # Check times against None, because midnight is represented by 0.
        return (self.start_time is not None and
                self.end_time is not None and
                self.start_time.strftime("%p") == self.end_time.strftime("%p"))

    def __unicode__(self):
        """This event, as a unicode string.

        :returns: The title of the event
        :rtype: str
        """
        return self.title

    def __repr__(self):
        """The representation of this event.

        :returns: The event's details.
        :rtype: str
        """
        return 'Event(title=%r, location=%r, creator=%r, start=%r, end=%r, ' \
            'published=%r)' % (self.title,
                               self.location, self.creator,
                               self.start_datetime(),
                               self.end_datetime(),
                               self.published)
