import datetime as dt

import pytest

from eventum.models import Event


@pytest.mark.parametrize(["sdate", "stime", "edate", "etime", "output"], [
    (    # Multi-day event
         dt.date(2015, 3, 31), dt.time(23),
         dt.date(2015, 4, 1), dt.time(3),
         'Tuesday, March 31 11pm - Wednesday, April 1 3am'
    ),
    (   # Multi-day event that shares am/pm
        dt.date(2015, 3, 31), dt.time(23),
        dt.date(2015, 4, 1), dt.time(23),
        'Tuesday, March 31 11pm - Wednesday, April 1 11pm'
    ),
    (   # Single day event
        dt.date(2015, 3, 31), dt.time(11, 0),
        dt.date(2015, 3, 31), dt.time(14, 15),
        'Tuesday, March 31 11am-2:15pm'
    ),
    (   # Single day event that shares am/pm
        dt.date(2015, 3, 31), dt.time(15, 0),
        dt.date(2015, 3, 31), dt.time(19, 30),
        'Tuesday, March 31 3-7:30pm'
    ),
    (   # None start dt.date
        None, dt.time(23),
        dt.date(2015, 4, 1), dt.time(3),
        '???, ??/?? 11pm - Wednesday, April 1 3am'
    ),
    (   # None start dt.time
        dt.date(2015, 3, 31), None,
        dt.date(2015, 4, 1), dt.time(3),
        'Tuesday, March 31 ??:?? - Wednesday, April 1 3am'
    ),
    (   # None end dt.date
        dt.date(2015, 3, 31), dt.time(23),
        None, dt.time(3),
        'Tuesday, March 31 11pm - ???, ??/?? 3am'
    ),
    (   # None start dt.time
        dt.date(2015, 3, 31), dt.time(23),
        dt.date(2015, 4, 1), None,
        'Tuesday, March 31 11pm - Wednesday, April 1 ??:??'
    ),
    (   # Single day event with None start dt.time
        dt.date(2015, 3, 31), None,
        dt.date(2015, 3, 31), dt.time(19, 30),
        'Tuesday, March 31 ??:??-7:30pm'
    ),
    (   # Single day event with None end dt.time
        dt.date(2015, 3, 31), dt.time(15, 0),
        dt.date(2015, 3, 31), None,
        'Tuesday, March 31 3pm-??:??'
    ),
])
def test_human_readable_atetime(sdate, stime, edate, etime, output):
    """Test that :func:`~app.models.Event.human_readable.datetime`
    properly formats event dates and times into human readable datetime
    strings.
    """

    event = Event(start_date=sdate, start_time=stime,
                  end_date=edate, end_time=etime)
    assert event.human_readable_datetime() == output


@pytest.mark.parametrize(["date", "output"], [
    (dt.date(2015, 3, 31), 'Tuesday, March 31'),
    (dt.date(2015, 4, 1), 'Wednesday, April 1'),
    (None, '??? ??/??')
])
def test_human_readable_date(date, output):
    """Test that :func:`~app.models.Event.human_readable_date` properly
    formats event dates into human readable date strings.
    """
    event = Event(start_date=date, start_time=None,
                  end_date=date, end_time=None)
    assert event.human_readable_date() == output


@pytest.mark.parametrize(["start_time", "end_time", "output"], [
    (dt.time(23), dt.time(3, 30), '11pm-3:30am'),
    (dt.time(21), dt.time(22), '9-10pm'),
    (None, dt.time(3, 30), '??:??-3:30am'),
    (dt.time(23), None, '11pm-??:??'),
    (None, None, '??:??-??:??'),
])
def test_human_readable_time(start_time, end_time, output):
    """Test that :func:`~app.models.Event.human_readable_time` properly
    formats event times into human readable time strings.
    """
    any_date = dt.date(2015, 3, 31)
    event = Event(start_date=any_date, start_time=start_time,
                  end_date=any_date, end_time=end_time)
    assert event.human_readable_time() == output


def test_event_ending_on_midnight():
    """Test that events ending on midnight are properly formatted."""
    start_date, start_time = dt.date(2015, 3, 31), dt.time(22)
    end_date, end_time = dt.date(2015, 4, 1), dt.time(0)

    event = Event(start_date=start_date,
                  start_time=start_time,
                  end_date=end_date,
                  end_time=end_time)

    assert not event.is_multiday()
    assert event.human_readable_date() == "Tuesday, March 31"
    assert event.human_readable_time() == "10pm-12am"


def test_event_starting_on_midnight():
    """Test that events starting on midnight are properly formatted."""
    event = Event(start_date=dt.date(2015, 4, 1),
                  start_time=dt.time(0),
                  end_date=dt.date(2015, 4, 1),
                  end_time=dt.time(5, 30))

    assert not event.is_multiday()
    assert event.human_readable_date() == "Wednesday, April 1"
    assert event.human_readable_time() == "12-5:30am"
