from app import db
from datetime import datetime
from mongoengine import ValidationError
now = datetime.now

USER_TYPES = {
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
    date_modified = db.DateTimeField(
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
        required=True, verbose_name="Privileges", default={
            "edit": False,
            "publish": False,
            "admin": False
        }, help_text="A dictionary of privileges and whether the user has \
        them.  To use one of the predefined sets of privileges, set this \
        value to either 'editor', 'publisher', or 'admin'.  This will be \
        converted to the appropriate dictionary on save.")
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

        # If self.privileges is one of the USER_TYPES keys, set that dictionary
        # to self.privileges
        if type(self.privileges) == str:
            if self.privileges in USER_TYPES:
                self.privileges = USER_TYPES[self.privileges]
            else:
                raise ValidationError("privelages should be a dictionary or \
                                      'editor' or 'publisher' or 'admin'.")

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
