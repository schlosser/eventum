from pyrfc3339 import generate
import pytz
import re
from app.lib.error import GoogleCalendarAPIError

class GoogleCalendarResourceBuilder():

    EASTERN = pytz.timezone('US/Eastern')

    @classmethod
    def event_resource(klass, event, for_update=False):
        """"""
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
        """"""
        r = 'RRULE:FREQ=%s' % s.frequency.upper()
        if s.every > 1:
            r += ';INTERVAL=%d' % s.every
        if s.ends_on:
            r += ';UNTIL=%s' % klass._recurrence_end_date(s)
        elif s.ends_after:
            r += ';COUNT=%d' % s.num_occurances
        else:
            raise GoogleCalendarAPIError('series should either end on or after')
        return r

    @classmethod
    def _recurrence_end_date(klass, s):
        """"""
        d = s.recurrence_end_date
        return '%d%02d%02dT235959Z' % (d.year, d.month, d.day)

    @classmethod
    def _strip_tags(klass, html):
        p = re.compile(r'<.*?>')
        return p.sub(' ', html)

    @classmethod
    def rfc3339(klass, datetime):
        """"""
        datetime_localized = klass.EASTERN.localize(datetime)
        return generate(datetime_localized, utc=False)
