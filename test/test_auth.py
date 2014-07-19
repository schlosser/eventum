import base
from mongoengine import ValidationError, NotUniqueError

from sys import path
path.append('../')

from app.models import User, Whitelist

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

    def setUp(self):
        for w in Whitelist.objects():
            w.delete()
        super(TestAuth, self).setUp()

    def test_login_route_logged_in(self):
        """Test the `/login` route while already logged in."""
        resp = self.request_with_role('/login', role='user',
                                      follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_login_route_logged_out(self):
        """Test the `/login` route logged out."""
        resp = self.request_with_role('/login', role='none')
        self.assertEqual(resp.status_code, 200)

    def test_create_profile_route_logged_in(self):
        """Test the `/create-profile` route while already logged in."""
        resp = self.request_with_role('/create-profile', role='user',
                                      follow_redirects=True,
                                      query_string=CREATE_PROFILE_QUERY_DATA)
        self.assertEqual(resp.status_code, 200)

    def test_create_profile_route_logged_out(self):
        """Test the `/create-profile` route logged out."""
        resp = self.request_with_role('/create-profile', role='none',
                                      query_string=CREATE_PROFILE_QUERY_DATA)
        self.assertEqual(resp.status_code, 200)

    def test_logout_route_logged_in(self):
        """Test the `/logout` route logged in."""
        resp = self.request_with_role('/logout', role='user')
        self.assertEqual(resp.status_code, 302)

    def test_logout_route_logged_out(self):
        """Test the `/logout` route logged out."""
        resp = self.request_with_role('/logout', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_users_route_logged_in(self):
        """Test the `/users` route logged in."""
        resp = self.request_with_role('/users', role='user')
        self.assertEqual(resp.status_code, 200)

    def test_users_route_logged_out(self):
        """Test the `/users` route logged out."""
        resp = self.request_with_role('/users', role='none')
        self.assertEqual(resp.status_code, 302)

    def test_user_declaration_with_missing_name(self):
        """Tests creation of a User model without the name param"""
        with self.assertRaises(ValidationError):
            u = User(email="test@te.st", gplus_id='test123')
            u.save()

    def test_user_declaration_with_missing_email(self):
        """Tests creation of a User model without the email param"""
        with self.assertRaises(ValidationError):
            u = User(name="Test User", gplus_id='test123')
            u.save()

    def test_user_declaration_with_missing_gplus_id(self):
        """Tests creation of a User model without the gplus_id param"""
        with self.assertRaises(ValidationError):
            u = User(name="Test User", email='test@te.st')
            u.save()

    def test_user_declaration_with_invalid_email_address(self):
        """Tests creation of a User model with invalid email address"""
        with self.assertRaises(ValidationError):
            u = User(name="Test User", email='bademail', gplus_id='test123')
            u.save()

    def test_user_declaration_with_invalid_privileges_string(self):
        """Tests creation of a User model with invalid privileges string"""
        with self.assertRaises(ValidationError):
            u = User(name="Test User", email='test@te.st', gplus_id='test123',
                     privileges='badvalue')
            u.save()

    def test_user_declaration_with_non_unique_email_address(self):
        """Tests creation of a User model with a non-unique email address"""
        with self.assertRaises(NotUniqueError):
            a = User(name="Test User", email="test@te.st", gplus_id='test123')
            a.save()
            b = User(name="Test User", email="test@te.st", gplus_id='test456')
            b.save()
        User.objects().delete()

    def test_user_declaration_with_non_unique_gplus_id(self):
        """Tests creation of a User model with a non-unique gplus_id address"""
        with self.assertRaises(NotUniqueError):
            a = User(name="Test User", email="test@te.st", gplus_id='test123')
            a.save()
            b = User(name="Test User", email="test@go.od", gplus_id='test123')
            b.save()
        User.objects().delete()

    def test_can(self):
        """Tests the User.can() method for privileges access"""
        user = User(name='Test Editor',
                    email='some_editor@te.st',
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

    def test_empty_user_type_alias(self):
        """ Test that an empty User model user_type field results in no
        privileges.
        """
        User.objects().delete()
        self.assertEqual(User.objects().count(), 0)
        u = User(name='Test User',
                 email='anotheruser@te.st',
                 gplus_id='user1234')
        u.save()
        self.assertDictContainsSubset(u.privileges, USER_PRIVILEGES['user'])

    def test_editor_user_type_alias(self):
        """ Test that passing `editor` into the User model user_type field
        results in editing privileges.
        """
        e = User(name='Test Editor',
                 email='anothereditor@te.st',
                 user_type='editor',
                 gplus_id='editor1234')
        e.save()
        self.assertDictContainsSubset(e.privileges, USER_PRIVILEGES['editor'])

    def test_publisher_user_type_alias(self):
        """ Test that passing `publisher` into the User model user_type field
        results in publishing privileges.
        """
        p = User(name='Test Publisher',
                 email='anotherpublisher@te.st',
                 user_type='publisher',
                 gplus_id='publisher1234')
        p.save()
        self.assertDictContainsSubset(p.privileges,
                                      USER_PRIVILEGES['publisher'])

    def test_admin_user_type_alias(self):
        """ Test that passing `admin` into the User model user_type field
        results in admin privileges.
        """
        a = User(name='Test Admin',
                 email='anotheradmin@te.st',
                 user_type='admin',
                 gplus_id='admin1234')
        a.save()
        self.assertDictContainsSubset(a.privileges, USER_PRIVILEGES['admin'])

    def test_whitelist_add_invalid_email(self):
        """Test that when an invalid email is provided, no user is added to the
        whitelist.
        """
        query_string_data = {
            "email": "notanemail",
            "user_type": "user"
        }
        resp = self.request_with_role('/whitelist/add',
                                      method='POST',
                                      query_string=query_string_data,
                                      follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Whitelist.objects().count(), 0)

    def test_whitelist_add_no_user_type(self):
        """Test that when no user type is provided, then no user is added to
        the whitelist.
        """
        query_string_data = {
            "email": "email@address.com",
            "user_type": None
        }
        resp = self.request_with_role('/whitelist/add',
                                      method='POST',
                                      query_string=query_string_data,
                                      follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Whitelist.objects().count(), 0)

    def test_whitelist_add_valid_input(self):
        """Test that when valid input is provided, a user is added to the
        whitelist.
        """
        query_string_data = {
            "email": "email@address.com",
            "user_type": "user"
        }
        resp = self.request_with_role('/whitelist/add',
                                      method='POST',
                                      data=query_string_data,
                                      follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Whitelist.objects().count(), 1)
        user = Whitelist.objects().get(email="email@address.com")
        self.assertEqual(user.user_type, "user")

    def test_whitelist_add_duplicate_email(self):
        """Test that when a duplicate email is added to the whitelist it is
        rejected.
        """
        query_string_data_1 = {
            "email": "email@address.com",
            "user_type": "user"
        }
        query_string_data_2 = {
            "email": "email@address.com",
            "user_type": "editor"
        }
        self.request_with_role('/whitelist/add',
                               method='POST',
                               data=query_string_data_1,
                               follow_redirects=True)

        resp = self.request_with_role('/whitelist/add',
                                      method='POST',
                                      data=query_string_data_2,
                                      follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Whitelist.objects().count(), 1)
        wl = Whitelist.objects().get(email="email@address.com")
        self.assertEqual(wl.user_type, "user")

    def test_whitelist_add_email_of_existing_user(self):
        """Test that when a email is added to the whitelist that belongs to
        an existing user, it should be rejected.
        """
        # Add a user to the database
        user = User(name="Test User", email="email@address.com",
                    gplus_id="test123", user_type="admin")
        user.save()
        self.assertEqual(User.objects(email="email@address.com").count(), 1)

        # Post a new whitelist entry
        query_string_data = {
            "email": "email@address.com",
            "user_type": "user"
        }
        resp = self.request_with_role('/whitelist/add',
                                      method='POST',
                                      data=query_string_data,
                                      follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Whitelist.objects().count(), 0)

    def test_whitelist_revoke(self):
        """Test removing an email from the waitlist.

        Adds num_trials emails to the whitelist, deletes some of them,
        and checks to make sure the right ones were deleted."""
        num_trials = 20
        # Post `num_trials` new whitelist entries
        for i in range(num_trials):
            query_string_data = {
                "email": "email%r@address.com" % i,
                "user_type": "user"
            }
            resp = self.request_with_role('/whitelist/add',
                                          method='POST',
                                          data=query_string_data,
                                          follow_redirects=True)

            # No error pages
            self.assertEqual(resp.status_code, 200)

        # `num_trials` whitelist items added.
        self.assertEqual(Whitelist.objects().count(), num_trials)

        delete = [i for i in range(num_trials) if i % 3 == 0]
        for i in range(num_trials):
            if i in delete:
                resp = self.request_with_role(
                    '/whitelist/delete/email%r@address.com' % i,
                    method='POST')
                self.assertEqual(resp.status_code, 200)

        for i in range(num_trials):
            in_list = Whitelist.objects(
                email="email%r@address.com" % i).count() == 1
            if i in delete:
                self.assertFalse(in_list)
            else:
                self.assertTrue(in_list)

    def test_users_delete(self):
        """Test that POSTing to `/users/delete` with an `email` in the form
        results in the user with that email being deleted.
        """
        query_string_data = {
            "email": "email@address.com"
        }
        resp = self.request_with_role('/users/delete',
                                      method='POST',
                                      data=query_string_data)

        self.assertEqual(resp.status_code, 303)

    def test_users_delete_with_no_such_user(self):
        """Test that POSTing to `/users/delete` with an `email` in the form
        that does not correspond to any user in the database does not result
        in any deletion of users.
        """
        # Add user to the database
        user = User(name="Test User", email="email@address.com",
                    gplus_id="test123", user_type="admin")
        user.save()
        num_users = User.objects().count()

        # Attempt to delete another user
        query_string_data = {
            "email": "anotheremail@address.com"
        }
        resp = self.request_with_role('/users/delete',
                                      method='POST',
                                      data=query_string_data)

        self.assertEqual(resp.status_code, 303)
        self.assertEqual(User.objects().count(), num_users)


if __name__ == '__main__':
    base.TestingTemplate.main()
