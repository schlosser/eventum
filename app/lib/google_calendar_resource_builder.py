from pyrfc3339 import generate
import pytz
from app.lib.error import GoogleCalendarAPIError

class GoogleCalendarResourceBuilder():

    EASTERN = pytz.timezone('US/Eastern')

    @classmethod
    def event_resource(klass, event):
        resource = {}
        resource['summary'] = event.title
        resource['location'] = event.location
        resource['description'] = event.long_description
        resource['status'] = 'confirmed' if event.is_published else 'tentative'

        rfc3339_start_dt = klass._rfc3339(event.start_datetime())
        rfc3339_end_dt = klass._rfc3339(event.end_datetime())

        resource['start'] = {}
        resource['start']['dateTime'] = rfc3339_start_dt
        resource['start']['timeZone'] = klass.EASTERN.zone
        resource['end'] = {}
        resource['end']['dateTime'] = rfc3339_end_dt
        resource['end']['timeZone'] = klass.EASTERN.zone
        return resource

    @classmethod
    def recurring_event_resource(klass, event):
        event_series = event.parent_series
        recurrence = klass._recurrence(event_series)

        resource = klass.event_resource(event)
        resource['recurrence'] = recurrence
        return resource

    @classmethod
    def _recurrence(klass, s):
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
        d = s.recurrence_end_date
        return '%d%d%dT235959Z' % (d.year, d.month, d.day)

    @classmethod
    def _rfc3339(klass, datetime):
        datetime_localized = klass.EASTERN.localize(datetime)
        return generate(datetime_localized, utc=False)
