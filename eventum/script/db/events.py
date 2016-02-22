"""
.. module:: events
    :synopsis: This module facilitates the generation of test event objects
        in the database.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import random
from datetime import datetime, timedelta
from mongoengine.queryset import DoesNotExist
from eventum.models import Image, Event, EventSeries
from lorem import LOREM_EVENT, LOREM_SNIPPET, LOREM_ADJECTIVES

TIMEDELTAS = [timedelta(hours=4),   # upcoming
              timedelta(hours=4),   # same time as ^
              timedelta(hours=-4),  # just happend
              ] + [timedelta(days=offset) for offset in range(-6, 6)]
RECURRING_SLUG = 'recurring'


def create_events(superuser, printer):
    """Creates several test events objects in the database, as well as a single
    recurring event series.

    :param superuser: The superuser object to associate with the events.
    :type superuser: :class:`~app.models.User`
    :param printer: The object to manage progress printing.
    :type printer: :class:`~script.cli.ProgressPrinter`

    :returns: A list of events and eventseries that now exist.
    :rtype: list(:class:`~app.models.Event` | :class:`~app.models.EventSeries`)
    """
    print 'Generating events...'
    printer.line()
    generator = EventGenerator(superuser, printer)
    datetimes = (datetime.now() + d for d in TIMEDELTAS)
    successes, skips, failures = generator.create_events(datetimes)
    printer.line()
    printer.results(len(successes), len(skips), len(failures))
    made = successes + skips

    print 'Generating event series...'
    generator = EventGenerator(superuser, printer)
    printer.line()
    successes, skips, failures = generator.create_weekly_event()
    printer.line()
    printer.results(len(successes), len(skips), len(failures))
    made += successes + skips

    return made


class EventGenerator():
    """Facilitates the generation of blog posts. Intended use:

        generator = PostGenerator(superuser, printer)
        successes, skips, failures = generator.create_posts(datetimes)

    """

    def __init__(self, superuser, printer):
        """Initialize the EventGenerator.

        :param superuser: The superuser object to associate with the images.
        :type superuser: :class:`~app.models.User`
        :param printer: The object to manage progress printing.
        :type printer: :class:`~script.cli.ProgressPrinter`
        """
        self.superuser = superuser
        self.printer = printer
        self.is_recurring = False
        self.index = 0
        self.successes = []
        self.failures = []
        self.skips = []

    def next(self, slug=None, **kwargs):
        """Create the next :class:`~app.models.Event` object if it doesn't
        already exist and then add it to ``self.successes`` or ``self.skips``
        appropriately.

        :param str slug: slug to override ``self._slug()``
        :param **kwargs: extra configuration overrides to be passed to the
            :class:`~app.models.Event` constructor.

        :returns: The created Event
        :rtype: :class:`~app.models.Event`
        """
        self.index += 1

        # Create and return the event
        slug = slug if slug else self._slug()
        self.printer.begin_status_line('<Event slug="{}">'.format(slug))
        try:
            event = Event.objects.get(slug=slug,
                                      start_date=self.start_datetime.date())
            self.skips.append(event)
            self.printer.status_skip()
        except DoesNotExist:
            event = self.make_event(slug=slug, **kwargs)
            event.save()
            self.successes.append(event)
            self.printer.status_success()
        return event

    def create_events(self, start_datetimes):
        """Creates several events, one for each of the ``start_datetimes``
        passed to this function.

        :param start_datetimes: The start datetimes of each of the posts that
            will be made.
        :type datetimes: list(:class:`datetime.datetime`)

        :returns: 3-tuple of (successes, skips, failures)
        :rtype: tuple(list(:class:`~app.models.Event`))
        """
        for dt in start_datetimes:
            self.start_datetime = dt
            self.next()
        return self.successes, self.skips, self.failures

    def create_weekly_event(self, num_events=12):
        """Creates a weekly recurring event with ``num_events`` entries,
        centered around todays date.

        :param int num_events: The number of occurrences for the series.

        :returns: 3-tuple of (successes, skips, failures)
        :rtype: tuple(list(:class:`~app.models.Event` |
                           :class:`~app.models.EventSeries`))
        """
        self.is_recurring = True
        slug = RECURRING_SLUG
        self.printer.begin_status_line('<EventSeries slug="{}">'.format(slug))
        try:
            series = EventSeries.objects.get(slug=slug)
            self.skips.append(series)
            self.printer.status_skip()
        except DoesNotExist:
            series = self.make_series(slug, num_events)
            series.save()
            self.successes.append(series)
            self.printer.status_success()

        date = datetime.now() - timedelta(days=num_events / 2 * 7)
        for i in range(num_events):
            # increment datetime
            self.start_datetime = date + timedelta(days=7 * i)
            # make the next event
            event = self.next(slug=slug, parent_series=series)
            event.save()
            # add the event to the series
            series.events.append(event)

        series.save()

        return self.successes, self.skips, self.failures

    def make_series(self, slug, num_events):
        """Create and return a new :class:`~app.models.EventSeries` object
        using the configuration variables on the ``self`` and any passed
        configurations.

        :param str slug: slug for the series
        :param int num_events: number of occurrences for the series

        :returns: The blog post.
        :rtype: :class:`~app.models.Event`
        """
        return EventSeries(frequency='weekly',
                           every=1,
                           slug=slug,
                           ends_on=False,
                           ends_after=True,
                           num_occurrences=num_events,
                           recurrence_summary=self._recurrence_summary())

    def make_event(self, slug, **kwargs):
        """Create and return a new :class:`~app.models.Event` object using
        the configuration variables on the ``self`` and any passed overrides.

        :param str slug: slug to override ``self._slug()``
        :param **kwargs: extra configuration overrides to be passed to the
            :class:`~app.models.Event` constructor.

        :returns: The blog post.
        :rtype: :class:`~app.models.Event`
        """
        return Event(title=self._title(),
                     creator=self.superuser,
                     location=self._location(),
                     slug=slug,
                     start_date=self._start_date(),
                     end_date=self._end_date(),
                     start_time=self._start_time(),
                     end_time=self._end_time(),
                     short_description_markdown=LOREM_SNIPPET,
                     long_description_markdown=LOREM_EVENT,
                     published=True,
                     date_published=self._date_published(),
                     is_recurring=self.is_recurring,
                     image=self._image(),
                     facebook_url=self._facebook_url(),
                     **kwargs)

    def _title(self):
        """Get the next event title.

        :returns: The title.
        :rtype: str
        """
        return '{} Test Event {}'.format(random.choice(LOREM_ADJECTIVES),
                                         self.index)

    def _slug(self):
        """Get the next event slug.

        :returns: The slug.
        :rtype: str
        """
        return 'test-event-{}'.format(self.index)

    def _location(self):
        """Get the location.

        :returns: The location.
        :rtype: str
        """
        return 'Some {} place'.format(
            random.choice(LOREM_ADJECTIVES).lower())

    def _start_date(self):
        """Get the start date from ``self.start_datetime``.

        :returns: The start date.
        :rtype: :class:`datetime.date`
        """
        return self.start_datetime.date()

    def _end_date(self):
        """Get the end date, which is 1hr from the start time.

        :returns:
        :rtype: :class:`datetime.date`
        """
        return (self.start_datetime + timedelta(hours=1)).date()

    def _start_time(self):
        """Get the start date from ``self.start_datetime``.

        :returns: The start time.
        :rtype: :class:`datetime.time`
        """
        return self.start_datetime.time()

    def _end_time(self):
        """Get the end time, which is 1hr from the start time.

        :returns: The end time.
        :rtype: :class:`datetime.time`
        """
        return (self.start_datetime + timedelta(hours=1)).time()

    def _date_published(self):
        """Gets the published date, which is a week before the event starts.

        :returns: The date published.
        :rtype: :class:`datetime.datetime`
        """
        return self.start_datetime - timedelta(days=7)

    def _recurrence_summary(self):
        """The recurrence summary for the recurrence GUI. This can be any
        garbage value.  It will be overwritten if any changes are made to the
        event.

        :returns: Dummy string
        :rtype: str
        """
        return 'Test recurrence'

    def _facebook_url(self):
        """Get the next Facebook URL.

        :returns: The URL.
        :rtype: str
        """
        return 'https://www.facebook.com/ADICU#idx={}'.format(self.index)

    def _image(self):
        """Gets an image to associate with the event, from the database.

        :returns: The image.
        :rtype: :class:'~app.models.Image'
        """
        return random.choice(Image.objects())

    def _event_image(self):
        """The filename of ``self._image()``.

        :returns: The filename.
        :rtype: str
        """
        image = self._image()
        return image.filename if image else ''
