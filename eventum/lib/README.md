# `/app/lib`

Helpers and libraries.

## Notable files

- `decorators.py`: Any Flask route decorators should go in here.
- `events.py`: Manages the arduous process of converting between event forms ([WTForms][wtforms]) and models ([Mongoengine][mongoengine])
- `google_calendar.py`: Eventum's Google Calendar API client.  Makes requests to the [Google Calendar API][google-calendar-api].

[google-calendar-api]: https://developers.google.com/google-apps/calendar/
[mongoengine]: http://docs.mongoengine.org/
[wtforms]: http://wtforms.readthedocs.org/en/latest/
