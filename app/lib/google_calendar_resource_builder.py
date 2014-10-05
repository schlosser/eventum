from pyrfc3339 import generate
import pytz
import re
from app.lib.error import GoogleCalendarAPIError

class GoogleCalendarResourceBuilder():

    EASTERN = pytz.timezone('US/Eastern')

    @classmethod
    def event_resource(klass, event, for_update=False):
        """Create an event resource to send in the body of a Google Calendar
        API request.

        :param event: The event to translate to an event resource.
        :type event: :class:`Event`
        :param bool for_update: True if the resource is being used in a call to
            update Google Calendar (in which case an extra ``sequence`` field
            is required).

        :raises: GoogleCalendarAPIError

        :returns: An event resource
        :rtype: dict
        """

        resource = {}
        resource['summary'] = event.title
        resource['location'] = event.location
        resource['description'] = klass._strip_tags(event.long_description)
        resource['status'] = 'confirmed' if event.published else 'tentative'
        if for_update:
            resource['sequence'] = event.gcal_sequence + 1

        rfc3339_start_dt = klass.rfc3339(event.start_datetime())
        rfc3339_end_dt = klass.rfc3339(event.end_datetime())

        resource['start'] = {}
        resource['start']['dateTime'] = rfc3339_start_dt
        resource['start']['timeZone'] = klass.EASTERN.zone
        resource['end'] = {}
        resource['end']['dateTime'] = rfc3339_end_dt
        resource['end']['timeZone'] = klass.EASTERN.zone

        if event.is_recurring:
            recurrence = klass._recurrence(event.parent_series)
            resource['recurrence'] = [recurrence]

        return resource

    @classmethod
    def _recurrence(klass, s):
        """Returns the RRULE recurrence for the given event series.

        :param s: The event series to translate to an RRULE string.
        :type s: :class:`EventSeries`

        :raises: GoogleCalendarAPIError

        :returns: The RRULE string
        :rtype: str
        """

        r = 'RRULE:FREQ=%s' % s.frequency.upper()
        if s.every > 1:
            r += ';INTERVAL=%d' % s.every
        if s.ends_on:
            r += ';UNTIL=%s' % klass._recurrence_end_date(s)
        elif s.ends_after:
            r += ';COUNT=%d' % s.num_occurrences
        else:
            raise GoogleCalendarAPIError('series should either end on or after')
        return r

    @classmethod
    def _recurrence_end_date(klass, s):
        """Returns the end date of the RRULE recurrence for the given event
        series.

        :param s: The event series to translate to an RRULE string.
        :type s: :class:`EventSeries`

        :returns: The end date as a string
        :rtype: str
        """
        d = s.recurrence_end_date
        return '%d%02d%02dT235959Z' % (d.year, d.month, d.day)

    @classmethod
    def _strip_tags(klass, html):
        """Strips the tags out of ``html``

        :param str html: The HTML string to clean

        :returns: The cleaned string
        :rtype: str
        """

        p = re.compile(r'<.*?>')
        return p.sub(' ', html)

    @classmethod
    def rfc3339(klass, datetime):
        """Returns ``datetime`` formatted as a rfc3339 string.

        :param datetime datetime: The date time to convert

        :returns: the rfc3339 formatted string
        :rtype: str
        """

        datetime_localized = klass.EASTERN.localize(datetime)
        return generate(datetime_localized, utc=False)
