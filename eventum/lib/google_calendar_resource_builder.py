from pyrfc3339 import generate
import pytz
from eventum.lib.text import clean_markdown
from eventum.lib.error import EventumError


class GoogleCalendarResourceBuilder():

    EASTERN = pytz.timezone('US/Eastern')

    @classmethod
    def event_resource(cls, event, for_update=False):
        """Create an event resource to send in the body of a Google Calendar
        API request.

        :param event: The event to translate to an event resource.
        :type event: :class:`Event`
        :param bool for_update: True if the resource is being used in a call to
            update Google Calendar (in which case an extra ``sequence`` field
            is required).

        :raises: :class:`EventumError.GCalAPI.EventMustEndOnOrAfter`

        :returns: An event resource
        :rtype: dict
        """

        resource = {}
        resource['summary'] = event.title
        resource['location'] = event.location
        resource['description'] = clean_markdown(
            event.long_description_markdown
        )
        resource['status'] = 'confirmed' if event.published else 'tentative'
        if for_update:
            resource['sequence'] = event.gcal_sequence + 1

        rfc3339_start_dt = cls.rfc3339(event.start_datetime)
        rfc3339_end_dt = cls.rfc3339(event.end_datetime)

        resource['start'] = {}
        resource['start']['dateTime'] = rfc3339_start_dt
        resource['start']['timeZone'] = cls.EASTERN.zone
        resource['end'] = {}
        resource['end']['dateTime'] = rfc3339_end_dt
        resource['end']['timeZone'] = cls.EASTERN.zone

        if event.is_recurring:
            recurrence = cls._recurrence(event.parent_series)
            resource['recurrence'] = [recurrence]

        return resource

    @classmethod
    def _recurrence(cls, s):
        """Returns the RRULE recurrence for the given event series.

        :param s: The event series to translate to an RRULE string.
        :type s: :class:`EventSeries`

        :raises: GoogleCalendarAPIError

        :returns: The RRULE string
        :rtype: str
        """

        r = 'RRULE:FREQ={}'.format(s.frequency.upper())
        if s.every > 1:
            r += ';INTERVAL=%d' % s.every
        if s.ends_on:
            r += ';UNTIL={}'.format(cls._recurrence_end_date(s))
        elif s.ends_after:
            r += ';COUNT=%d' % s.num_occurrences
        else:
            raise EventumError.GCalAPI.EventMustEndOnOrAfter()
        return r

    @classmethod
    def _recurrence_end_date(cls, s):
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
    def rfc3339(cls, datetime):
        """Returns ``datetime`` formatted as a rfc3339 string.

        :param datetime datetime: The date time to convert

        :returns: the rfc3339 formatted string
        :rtype: str
        """

        datetime_localized = cls.EASTERN.localize(datetime)
        return generate(datetime_localized, utc=False)
