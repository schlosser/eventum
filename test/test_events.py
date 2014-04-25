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

    def test_events_route(self):
        """Test the `/events` route, logged in and logged out."""

        # Logged in
        resp = self.request_with_role('/events', role='user')
        self.assertEqual(resp.status_code, 200)

        # Logged out
        resp = self.request_with_role('/events', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_create_event_route(self):
        """Test the `/events/create` route, logged in and logged out,
        with correct and incorrect privileges.
        """

        # Logged in with correct privileges
        resp = self.request_with_role('/events/create', role='editor')
        self.assertEqual(resp.status_code, 200)

        # Logged in, no edit privileges
        resp = self.request_with_role('/events/create', role='user')
        self.assertEqual(resp.status_code, 401)

        # Logged out
        resp = self.request_with_role('/events/create', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_create_event_model_missing_parameters(self):
        """Test creating an event without all the required parameters."""

        # Missing title
        someuser = User.objects().first()
        with self.assertRaises(ValidationError):
            e = Event(creator=someuser)
            e.save()

        # Missing creator
        with self.assertRaises(ValidationError):
            e = Event(title="Some Title")
            e.save()

    def test_create_event_model_with_backwards_dates(self):
        """Test creating an event with the start_datetime after the
        end_datetime.
        """
        someuser = User.objects().first()
        with self.assertRaises(ValidationError):
            e = Event(title="Some Title", creator=someuser,
                      end_date=datetime.now().date(),
                      start_date=datetime.now().date(),
                      end_time=datetime.now().time(),
                      start_time=datetime.now().time() + timedelta(minutes=1))
            e.save()

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

    def test_create_event_model_with_missing_dates_and_times(self):
        """Test that POSTing data with at least one date and/or time field missing
        results in no event data whatsoever."""



if __name__ == '__main__':
    base.TestingTemplate.main()
