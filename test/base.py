import unittest
import os
import mongoengine
from coverage import coverage
from sys import path
path.append('../')
from app import create_app
from app.mod_auth.models import User, Whitelist
from app.mod_events.models import Event
from config.flask_config import basedir

GPLUS_IDS = {
    'user': 'user123',
    'editor': 'editor123',
    'publisher': 'publisher123',
    'admin': 'admin123'
}


class TestingTemplate(unittest.TestCase):

    def setUp(self):
        for u in User.objects():
            u.delete()
        user= User(name='Test User',
                   email='user@te.st',
                     gplus_id=GPLUS_IDS['user'])
        editor= User(name='Test Editor',
                     email='editor@te.st',
                     user_type='editor',
                     gplus_id=GPLUS_IDS['editor'])
        publisher= User(name='Test Publisher',
                        email='publisher@te.st',
                        user_type='publisher',
                        gplus_id=GPLUS_IDS['publisher'])
        admin= User(name='Test Admin',
                    email='admin@te.st',
                    user_type='admin',
                    gplus_id=GPLUS_IDS['admin'])
        user.save()
        editor.save()
        publisher.save()
        admin.save()
        e = User.objects().get(gplus_id=GPLUS_IDS['editor'])
        print e.privileges

    @classmethod
    def setUpClass(self):
        """ Sets up a test database before each set of tests """
        create_app(
            MONGODB_SETTINGS={'DB': 'testing'},
            TESTING=True,
            CSRF_ENABLED=False,
            WTF_CSRF_ENABLED=False
        )
        from app import app
        self.app = app

    @classmethod
    def tearDownClass(self):
        """ Drops the test database after the classes' tests are finished"""

    def request_with_role(self, path, method='GET', role='admin',
                          *args, **kwargs):
        """ Make an http request with the given role's gplus_id
        in the session and a User with the given role in the database.
        """
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                if role in GPLUS_IDS:
                    # if it isn't, the request is without a role
                    sess['gplus_id'] = GPLUS_IDS[role]
                kwargs['method'] = method
                kwargs['path'] = path
            return c.open(*args, **kwargs)

    def test_create_test_app(self):
        self.assertTrue(self.app.config['TESTING'])
        self.assertFalse(self.app.config['CSRF_ENABLED'])
        self.assertEqual(mongoengine.connection.get_db().name, 'testing')

    @classmethod
    def main(self):
        cov = coverage(
            branch=True, omit=['../test.py', '../test/*', '../lib/*',
                               '../include/*', '../bin/*'])
        cov.start()
        try:
            unittest.main()
        except:
            pass
        cov.stop()
        cov.save()
        print "\n\nCoverage Report:\n"
        cov.report()
        print "HTML version: " + \
            os.path.join(basedir, "tmp/coverage/index.html")
        cov.html_report(directory='tmp/coverage')
        cov.erase()


if __name__ == '__main__':
    TestingTemplate.main()
