# `/script`

Helper scripts

## Notable files

- `backfill_blog.py`: A script to backfill the `eventum` mongo database from the old data. To get the old website data, run this:
    ```
    cd data
    git clone https://github.com/adicu/old-website-data
    ```
- `events.py`: Manages the arduous process of converting between event forms ([WTForms][wtforms]) and models ([Mongoengine][mongoengine])
- `google_calendar.py`: Eventum's Google Calendar API client.  Makes requests to the [Google Calendar API][google-calendar-api].

[google-calendar-api]: https://developers.google.com/google-apps/calendar/
[mongoengine]: http://docs.mongoengine.org/
[wtforms]: http://wtforms.readthedocs.org/en/latest/
