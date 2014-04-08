from app import db
from datetime import datetime
now = datetime.now


class User(db.Document):
    date_created = db.DateTimeField(
        default=now, required=True, verbose_name="Date Created",
        help_text="DateTime when the user was created, localized to the server")
    date_modified = db.DateTimeField(
        default=now, required=True, verbose_name="Date Modified",
        help_text="DateTime when the user was last modified, localized to the server")
    openid = db.StringField(
        required=True, verbose_name="Open ID",
        help_text="The Open ID of the user.")
    name = db.StringField(
        max_length=510, verbose_name="Full Name", required=True,
        help_text="Full name of the user (510 characters max)")
    email = db.EmailField(
        required=True, verbose_name="Email Address",
        help_text="Email address of the user")
    roles = db.ListField(
        db.StringField(
            db_field="role", verbose_name="Role",
            help_text="A role that the user hase"),
        verbose_name="Roles", default=list, help_text="A List of roles")
    privelages = db.DictField(
        required=True, verbose_name="Privelages", default={
            "edit": False,
            "publish": False,
            "admin": False
        }, help_text="A dictionary of privelages and whether the user has them")
    last_logon = db.DictField(
        verbose_name="Last Logon",
        help_text="Time of this user's last logon")

    def can(self, privelage):
        return self.privelages.get(privelage)

    def clean(self):
        """Update date_modified"""
        self.date_modified = now()

    meta = {
        'allow_inheritance': True,
        'indexes': ['email']
    }

    def __repr__(self):
        return 'User(name=%r, email=%r, roles=%r, privelages=%r)' % \
            (self.name, self.email, self.roles, self.privelages)

    def __unicode__(self):
        if self.can('admin'):
            return '%r <%r> (Admin)' % (self.name, self.email)
        if self.can('publish'):
            return '%r <%r> (Publisher)' % (self.name, self.email)
        if self.can('edit'):
            return '%r <%r> (Editor)' % (self.name, self.email)
        else:
            return '%r <%r>' % (self.name, self.email)
