import base
# from mongoengine import ValidationError, NotUniqueError

from sys import path
path.append('../')

from app.mod_events.models import Event

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
        dir(resp)
        self.assertEqual(resp.status_code, 302)

if __name__ == '__main__':
    base.TestingTemplate.main()
