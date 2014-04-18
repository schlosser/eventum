import base
from mongoengine import ValidationError, NotUniqueError

from sys import path
path.append('../')

from app.mod_auth.models import User

USER_PRIVILEGES = {
    "user": {
        "edit": False,
        "publish": False,
        "admin": False
    },
    "editor": {
        "edit": True,
        "publish": False,
        "admin": False
    },
    "publisher": {
        "edit": True,
        "publish": True,
        "admin": False
    },
    "admin": {
        "edit": True,
        "publish": True,
        "admin": True
    }
}

CREATE_PROFILE_QUERY_DATA = {
    'next': 'http://localhost:5000',
    'name': 'Test Admin',
    'email': 'admin@te.st',
    'image_url': 'http://kittens.com/cat/large'
}


class TestAuth(base.TestingTemplate):

    def test_login_route(self):
        """Test the `/login` route, logged in and logged out."""

        # Logged in
        resp = self.request_with_role('/login', role='user',
                                      follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Logged out
        resp = self.request_with_role('/login', role='none')
        self.assertEqual(resp.status_code, 200)

    def test_create_profile_route(self):
        """Test the `/create-profile` route, logged in and logged out."""

        # Logged in
        resp = self.request_with_role('/create-profile', role='user',
                                      follow_redirects=True,
                                      query_string=CREATE_PROFILE_QUERY_DATA)
        self.assertEqual(resp.status_code, 200)

        # Logged out
        resp = self.request_with_role('/create-profile', role='none',
                                      query_string=CREATE_PROFILE_QUERY_DATA)
        self.assertEqual(resp.status_code, 200)

    def test_logout_route(self):
        """Test the `/logout` route, logged in and logged out."""

        # Logged in
        resp = self.request_with_role('/logout', role='user')
        self.assertEqual(resp.status_code, 302)

        # Logged out
        resp = self.request_with_role('logout', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_user_declaration_with_missing_parameters(self):
        """Tests creation of a User model with missing parameters"""
        User.drop_collection()

        with self.assertRaises(ValidationError):
            u = User(email="test@te.st", gplus_id='test123')
            u.save()
        with self.assertRaises(ValidationError):
            u = User(name="Test User", gplus_id='test123')
            u.save()
        with self.assertRaises(ValidationError):
            u = User(name="Test User", email='test@te.st')
            u.save()

    def test_user_declaration_with_invalid_parameters(self):
        """Tests creation of a User model with invalid parameters"""
        User.drop_collection()

        # Invalid email address
        with self.assertRaises(ValidationError):
            u = User(name="Test User", email='bademail', gplus_id='test123')
            u.save()

        # Invalid privileges string (note that only a select few strings are
        # valid shorthands for the default dictionaries)
        with self.assertRaises(ValidationError):
            u = User(name="Test User", email='test@te.st', gplus_id='test123',
                     privileges='badvalue')
            u.save()

    def test_user_declaration_with_non_unique_parameters(self):
        """Tests creation of a User model with missing parameters"""
        User.drop_collection()

        # Non-unique email address
        with self.assertRaises(NotUniqueError):
            a = User(name="Test User", email="test@te.st", gplus_id='test123')
            a.save()
            b = User(name="Test User", email="test@te.st", gplus_id='test456')
            b.save()
        User.objects().delete()

        # Non-unique Google Plus ID
        with self.assertRaises(NotUniqueError):
            a = User(name="Test User", email="test@te.st", gplus_id='test123')
            a.save()
            b = User(name="Test User", email="test@go.od", gplus_id='test123')
            b.save()
        User.objects().delete()

    def test_can(self):
        """Tests the User.can() method for privileges access"""
        User.drop_collection()

        user = User(name='Test Editor',
                 email='editor@te.st',
                 privileges={
                     "edit": True,
                     "publish": True,
                     "admin": False,
                     "fly": False
                 },
                 gplus_id='editor1234')
        user.save()
        for k, v in user.privileges.iteritems():
            self.assertEqual(user.can(k), v)

    def test_user_privilege_aliases(self):
        """ Tests the User model privilege aliases and the can() method"""
        User.drop_collection()

        # No alias
        self.assertEqual(User.objects().count(), 0)
        u = User(name='Test User',
                 email='user@te.st',
                 gplus_id='user1234')
        u.save()
        self.assertDictContainsSubset(u.privileges, USER_PRIVILEGES['user'])

        # The `editor` alias
        e = User(name='Test Editor',
                 email='editor@te.st',
                 privileges='editor',
                 gplus_id='editor1234')
        e.save()
        self.assertDictContainsSubset(e.privileges, USER_PRIVILEGES['editor'])

        # The `publisher` alias
        p = User(name='Test Publisher',
                 email='publisher@te.st',
                 privileges='publisher',
                 gplus_id='publisher1234')
        p.save()
        self.assertDictContainsSubset(p.privileges,
                                      USER_PRIVILEGES['publisher'])

        # The `admin` alias
        a = User(name='Test Admin',
                 email='admin@te.st',
                 privileges='admin',
                 gplus_id='admin1234')
        a.save()
        self.assertDictContainsSubset(a.privileges, USER_PRIVILEGES['admin'])


if __name__ == '__main__':
    base.TestingTemplate.main()
