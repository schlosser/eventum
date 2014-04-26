import base
from mongoengine import ValidationError
from datetime import datetime, timedelta

from sys import path
path.append('../')

from app.mod_events.models import Event
from app.mod_auth.models import User

class TestEvents(base.TestingTemplate):

    def setUp(self):
        for e in Event.objects():
            e.delete()
        super(TestEvents, self).setUp()

    def test_events_route_logged_in(self):
        """Test the `/events` route, logged in."""
        resp = self.request_with_role('/events', role='user')
        self.assertEqual(resp.status_code, 200)

    def test_events_route_logged_out(self):
        """Test the `/events` route, logged out."""
        resp = self.request_with_role('/events', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_create_event_route_with_correct_privileges(self):
        """Test the `/events/create` route, logged in with correct
        privileges.
        """
        resp = self.request_with_role('/events/create', role='editor')
        self.assertEqual(resp.status_code, 200)

    def test_create_event_route_with_incorrect_privileges(self):
        """Test the `/events/create` route, logged in with
        incorrect privileges.
        """
        resp = self.request_with_role('/events/create', role='user')
        self.assertEqual(resp.status_code, 401)

    def test_create_event_route_logged_out(self):
        """Test the `/events/create` route, logged out."""
        resp = self.request_with_role('/events/create', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_create_event_model_missing_title(self):
        """Test that creating an Event without a title fails."""
        someuser = User.objects().first()
        with self.assertRaises(ValidationError):
            e = Event(creator=someuser)
            e.save()

    def test_create_event_model_missing_creator(self):
        """Test that creating an Event without a creator fails."""
        with self.assertRaises(ValidationError):
            e = Event(title="Some Title")
            e.save()

    def test_create_event_model_with_backwards_dates(self):
        """Test creating an event with the start_datetime after the
        end_datetime.
        """
        someuser = User.objects().first()
        # Good dates, bad times
        with self.assertRaises(ValidationError):
            e = Event(title="Some Title", creator=someuser,
                      start_date=datetime.now().date(),
                      end_date=datetime.now().date(),
                      start_time=(datetime.now() + timedelta(minutes=1)).time(),
                      end_time=datetime.now().time())
            e.save()

        # Bad dates, good times
        with self.assertRaises(ValidationError):
            e = Event(title="Some Title", creator=someuser,
                      start_date=datetime.now().date() + timedelta(days=1),
                      end_date=datetime.now().date(),
                      start_time=datetime.now().time(),
                      end_time=(datetime.now() + timedelta(minutes=1)).time())
            e.save()

    def test_event_start_datetimes_none_with_incomplete_data(self):
        """Test that when events are created without both of start_date and
        start_time, start_datetime() returns None.
        """
        someuser = User.objects().first()

        e = Event(title="Some Title", creator=someuser,
                  start_date=datetime.now().date())
        self.assertIsNone(e.start_datetime())

        f = Event(title="Some Title", creator=someuser,
                  start_time=datetime.now().time())
        self.assertIsNone(f.start_datetime())

    def test_event_end_datetimes_none_with_incomplete_data(self):
        """Test that when events are created without both of end_date and
        end_time, end_datetime() returns None.
        """
        someuser = User.objects().first()

        e = Event(title="Some Title", creator=someuser,
                  end_date=datetime.now().date())
        self.assertIsNone(e.end_datetime())

        f = Event(title="Some Title", creator=someuser,
                  end_time=datetime.now().time())
        self.assertIsNone(f.end_datetime())

    def test_create_event_model(self):
        """Test creating an event with the proper data"""
        someuser = User.objects().first()
        self.assertEqual(Event.objects(creator=someuser).count(), 0)
        e = Event(title="Some Title", creator=someuser,
                  end_datetime=datetime.now() + timedelta(minutes=1),
                  start_datetime=datetime.now())
        e.save()
        self.assertEqual(Event.objects(creator=someuser).count(), 1)
        self.assertEqual(Event.objects().get(creator=someuser), e)

    def test_create_event_model_using_form(self):
        """Test creating an event by POSTing data to the `/events/create`
        route.
        """
        query_string_data = {
            "title": "Test Title",
            "location": "45 Some Location",
            "start_date": "2014-02-15",
            "start_time": "12:15:00",
            "end_date": "2014-02-15",
            "end_time": "13:15:30",
            "short_description": "This is a short description.",
            "long_description": "This is a long description. It is longer"
        }

        self.assertEqual(Event.objects(location="45 Some Location").count(), 0)
        resp = self.request_with_role('/events/create',
            method='POST',
            data=query_string_data,
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects(location="45 Some Location").count(), 1)

    def test_create_event_model_using_form_without_title(self):
        """Test that POSTing event data to `/events/create` without a title does
        not result in event creation.
        """

        bad_data = {
            "location": "45 Some Location",
            "start_date": "2014-02-15",
            "start_time": "12:15:00",
            "end_date": "2014-02-15",
            "end_time": "13:15:30",
            "short_description": "This is a short description.",
            "long_description": "This is a long description. It is longer"
        }

        self.assertEqual(Event.objects(location="45 Some Location").count(), 0)
        resp = self.request_with_role('/events/create',
            method='POST',
            data=bad_data,
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Event.objects(location="45 Some Location").count(), 0)

    def test_delete_event(self):
        raise NotImplementedError

    def test_publish_as_publisher(self):
        raise NotImplementedError

    def test_publish_as_editor(self):
        raise NotImplementedError

    def test_unpublish_as_publisher(self):
        raise NotImplementedError

    def test_unpublish_as_editor(self):
        raise NotImplementedError


if __name__ == '__main__':
    base.TestingTemplate.main()
