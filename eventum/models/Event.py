"""
.. module:: Event
    :synopsis: An event database model.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import markdown
from flask import url_for, current_app
from datetime import datetime, timedelta
from mongoengine import (Document, DateTimeField, StringField, ReferenceField,
                         BooleanField, IntField, ValidationError)
from eventum.models.fields import DateField, TimeField
from eventum.models import BaseEventumDocument
now = datetime.now


class Event(Document, BaseEventumDocument):
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

    date_created = DateTimeField(required=True, default=now)
    date_modified = DateTimeField(required=True, default=now)
    title = StringField(required=True, max_length=255)
    creator = ReferenceField("User", required=True)
    location = StringField()
    slug = StringField(required=True, max_length=255)
    start_date = DateField()
    end_date = DateField()
    start_time = TimeField()
    end_time = TimeField()
    short_description = StringField()
    long_description = StringField()
    short_description_markdown = StringField()
    long_description_markdown = StringField()
    published = BooleanField(required=True, default=False)
    date_published = DateTimeField()
    is_recurring = BooleanField(required=True, default=False)
    parent_series = ReferenceField("EventSeries")
    image = ReferenceField("Image")
    facebook_url = StringField()
    gcal_id = StringField()
    gcal_sequence = IntField()

    def get_absolute_url(self):
        """Returns the URL path that points to the client-facing version of
        this event.

        :returns: A URL path like ``"/events/cookies-and-code"``.
        :rtype: str
        """
        if self.is_recurring:
            return url_for('client.recurring_event',
                           slug=self.slug,
                           index=self.index)
        return url_for('client.event', slug=self.slug)

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
            self.short_description = markdown.markdown(
                self.short_description_markdown,
                ['extra', 'smarty']
            )

        if self.long_description_markdown:
            self.long_description = markdown.markdown(
                self.long_description_markdown,
                ['extra', 'smarty']
            )

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

    @property
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

    @property
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

    def image_url(self):
        """Returns the URL path that points to the image for the event.

        :returns: The URL path like ``"/static/img/cat.jpg"``.
        :rtype: str
        """
        if self.image:
            return self.image.url()
        return url_for(
            'eventum.static',
            filename=current_app.config['EVENTUM_DEFAULT_EVENT_IMAGE'])

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
        return all([self.title,
                    self.creator,
                    self.location,
                    self.start_datetime,
                    self.end_datetime,
                    self.short_description,
                    self.long_description,
                    self.image])

    def is_multiday(self):
        """Returns True if the event spans muliple days.

        :returns: True if the event spans multiple days.
        :rtype: bool
        """
        if self.start_date is None or self.end_date is None:
            return True
        if self.start_date == self.end_date:
            return False
        if (self.start_date == self.end_date - timedelta(days=1) and
                self.end_time.hour < 5):
            return False
        return True

    def human_readable_date(self):
        """Return the date of the event (presumed not multiday) formatted like:
        ``"Sunday, March 31"``.

        :returns: The formatted date.
        :rtype: str
        """
        if not self.start_date:
            return '??? ??/??'
        return self.start_date.strftime("%A, %B %d").replace(' 0', ' ')

    def human_readable_time(self):
        """Return the time range of the event (presumed not multiday) formatted
        like ``"11am - 2:15pm"`` or ``"3 - 7:30pm"``.

        :returns: The formatted date.
        :rtype: str
        """
        return '{}-{}'.format(self._human_readable_start_time(),
                              self._human_readable_end_time())

    def _human_readable_start_time(self):
        """Format start time as one of these four formats:

        1. ``"3:30am"``
        2. ``"3pm"``
        2. ``"3:30"``
        2. ``"3"``

        depending on whether or not the start time is on an even hour, and
        whether or not the end time and start time will share the pm/am string.

        :returns: The formatted date.
        :rtype: str
        """
        if self.start_time is None:
            return '??:??'

        am_pm = '%p'
        if self._start_and_end_time_share_am_or_pm():
            am_pm = ''   # Omit am/pm if it will appear in the end time.

        time = '%I:%M'
        if self.start_time.minute == 0:
            time = '%I'  # Omit minutes if the time is on the hour.

        format = time + am_pm
        return self.start_time.strftime(format).lstrip('0').lower()

    def _human_readable_end_time(self):
        """Format end time as one of these two formats:

        1. ``"3:30am"``
        2. ``"3pm"``

        depending on whether or not the end time is on an even hour

        :returns: The formatted date.
        :rtype: str
        """
        if self.end_time is None:
            return '??:??'
        format = '%I:%M%p'
        if self.end_time.minute == 0:
            format = '%I%p'
        return self.end_time.strftime(format).lstrip('0').lower()

    def human_readable_datetime(self):
        """Format the start and end date date in one of the following three
        formats:

        1. ``"Sunday, March 31 11pm - Monday, April 1 3am"``
        2. ``"Sunday, March 31 11am-2:15pm"``
        3. ``"Sunday, March 31 3-7:30pm"``

        Depending on whether or not the start / end times / dates are the same.
        All unkown values will be replaced by question marks.

        :returns: The formatted date.
        :rtype: str
        """
        if self.start_date:
            start_date = (self.start_date.strftime('%A, %B %d ')
                          .replace(' 0', ' '))
        else:
            start_date = '???, ??/?? '

        # Check times against None, because midnight is represented by 0.
        if self.start_time is not None:
            start_time = self._human_readable_start_time()
        else:
            start_time = '??:??'

        if self.end_date:
            if not self.start_date or self.start_date != self.end_date:
                end_date = (self.end_date.strftime('%A, %B %d ')
                            .replace(' 0', ' '))
            else:
                end_date = ''
        else:
            end_date = '???, ??/?? '

        # Check times against None, because midnight is represented by 0.
        if self.end_time is not None:
            end_time = self._human_readable_end_time()
        else:
            end_time = '??:??'

        separator = ' - '
        if not end_date:
            separator = '-'

        return '{}{}{}{}{}'.format(start_date,
                                   start_time,
                                   separator,
                                   end_date,
                                   end_time)

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
                not self.is_multiday() and
                self.start_time.strftime("%p") == self.end_time.strftime("%p"))

    def to_jsonifiable(self):
        """
        Returns a jsonifiable dictionary of event attributes to values. The
        dictionary only contains attributes whose types are jsonifiable.

        :returns: A jsonifiable dictionary of event attributes to values.
        :rtype: dict
        """

        attrs = ['date_created', 'date_modified', 'title', 'location', 'slug',
                 'start_datetime', 'end_datetime', 'short_description',
                 'long_description', 'short_description_markdown',
                 'long_description_markdown', 'published', 'date_published',
                 'is_recurring', 'facebook_url']

        return dict(zip(list(attrs), [getattr(self, attr) for attr in attrs]))

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
            'published=%r)' % (self.title, self.location, self.creator,
                               self.start_datetime, self.end_datetime,
                               self.published)
