from pyrfc3339 import generate
import pytz


class GoogleCalendarResourceBuilder():

    def build_longform_from_event(klass, event):
        longform = {}
        longform['summary'] = event.title
        longform['location'] = event.location
        longform['description'] = event.description
        rfc3339_start_dt = klass.rfc3339(event.start_datetime())
        rfc3339_end_dt = klass.rfc3339(event.end_datetime())
        longform['start_date'] = {'dateTime': rfc3339_start_dt}
        longform['end_date'] = {'dateTime': rfc3339_end_dt}
        return longform

    @classmethod
    def rfc3339(self, datetime):
        generate(datetime.replace(tzinfo=pytz.utc))
