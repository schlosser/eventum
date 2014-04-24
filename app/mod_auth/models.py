from app import db
from datetime import datetime
now = datetime.now

USER_TYPES = {
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


class User(db.Document):
    date_created = db.DateTimeField(
        default=now, required=True, verbose_name="Date Created",
        help_text="DateTime when user was created, localized to the server")
    date_modified2 = db.DateTimeField(
        default=now, required=True, verbose_name="Date Modified",
        help_text="DateTime of last modification, localized to the server")
    gplus_id = db.StringField(
        required=True, verbose_name="Google Plus ID", unique=True,
        help_text="The Google Plus ID of the user")
    name = db.StringField(
        max_length=510, verbose_name="Full Name", required=True,
        help_text="Full name of the user (510 characters max)")
    email = db.EmailField(
        required=True, verbose_name="Email Address", unique=True,
        help_text="Email address of the user")
    roles = db.ListField(
        db.StringField(
            db_field="role", verbose_name="Role",
            help_text="A role that the user hase"),
        verbose_name="Roles", default=list, help_text="A List of roles")
    privileges = db.DictField(
        required=True, verbose_name="Privileges", default={},
        help_text="A dictionary of privileges and whether the user has \
        them.  To use one of the predefined sets of privileges, set this \
        value to either 'editor', 'publisher', or 'admin'.  This will be \
        converted to the appropriate dictionary on save.")
    image_url = db.URLField(
        verbose_name="Profile Image Url",
        help_text="URL to the user's profile picture.")
    user_type = db.StringField(
        verbose_name="User Type", default='user',
        regex="(user|editor|publisher|admin)",
        help_text="A shortcut for the privileges DictField")
    last_logon = db.DateTimeField(
        verbose_name="Last Logon",
        help_text="Time of this user's last logon")

    def can(self, privilege):
        """Returns whether or not the user has a privilege"""
        return self.privileges.get(privilege)

    def register_login(self):
        """Update the model as having logged in"""
        self.last_logon = now()

    def clean(self):
        """Update date_modified and apply privileges shorthand notation."""
        self.date_modified = now()

        # If undefined, update self.privileges with one of the USER_TYPES dictionaries
        if self.privileges == {}:
            self.privileges.update(USER_TYPES[self.user_type])

    meta = {
        'allow_inheritance': True,
        'indexes': ['email']
    }

    def __repr__(self):
        return 'User(name=%r, email=%r, roles=%r, privileges=%r, gplus_id=%r, date_created=%r)' % \
        (self.name, self.email, self.roles, self.privileges, self.gplus_id, self.date_created)

    def __unicode__(self):
        if self.can('admin'):
            return '%r <%r> (Admin)' % (self.name, self.email)
        if self.can('publish'):
            return '%r <%r> (Publisher)' % (self.name, self.email)
        if self.can('edit'):
            return '%r <%r> (Editor)' % (self.name, self.email)
        else:
            return '%r <%r>' % (self.name, self.email)


class Whitelist(db.Document):
    date_created = db.DateTimeField(
        default=now, required=True, verbose_name="Date Created",
        help_text="DateTime when user was created, localized to the server")
    date_modified = db.DateTimeField(
        default=now, required=True, verbose_name="Date Modified",
        help_text="DateTime of last modification, localized to the server")
    email = db.EmailField(
        required=True, verbose_name="Email Address", unique=True,
        help_text="Email address of the whitelisted user.")
    user_type = db.StringField(
        verbose_name="User Type",
        help_text="The type of user that will be created.")
    redeemed = db.BooleanField(
        default=False, required=True, verbose_name="Redeemed",
        help_text="Whether or not the whitelisted email has been redeemed, \
        and is associated with a user account or not.")

    def clean(self):
        """Update date_modified and apply privileges shorthand notation."""
        self.date_modified = now()

    meta = {
        'indexes': ['email']
    }

    def __repr__(self):
        return 'Whitelist(email=%r, user_type=%r, redeemed=%r)' % (self.email, self.user_type, self.redeemed)

    def __unicode__(self):
        return 'Whitelist<%r>' % self.email
