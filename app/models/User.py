import re
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
    """"""

    date_created = db.DateTimeField(required=True, default=now)
    date_modified = db.DateTimeField(required=True, default=now)
    gplus_id = db.StringField(required=True, unique=True)
    name = db.StringField(required=True, max_length=510)
    slug = db.StringField(required=True, max_length=510, unique=True,
                          regex='([a-z]|[A-Z]|[1-9]|-)*')
    email = db.EmailField(required=True, unique=True)
    roles = db.ListField(db.StringField(db_field="role"), default=list)
    privileges = db.DictField(required=True, default={})
    image_url = db.URLField()
    user_type = db.StringField(default='user',
                               regex="(user|editor|publisher|admin)")
    last_logon = db.DateTimeField()

    meta = {
        'allow_inheritance': True,
        'indexes': ['email', 'gplus_id']
    }

    def can(self, privilege):
        """Returns whether or not the user has a privilege"""
        return self.privileges.get(privilege)

    def get_profile_picture(self, size=50):
        if "googleusercontent.com" in self.image_url:
            return self.image_url + str(size)
        return self.image_url

    def register_login(self):
        """Update the model as having logged in"""
        self.last_logon = now()

    def clean(self):
        """Update date_modified and apply privileges shorthand notation."""
        self.date_modified = now()

        # If undefined, update self.privileges with one of the USER_TYPES
        # dictionaries
        if self.privileges == {}:
            self.privileges.update(USER_TYPES[self.user_type])

        # Update the slug for the user (used in URLs)
        new_slug = self.name.lower().replace(' ', '-')
        new_slug = re.sub(r"\'|\.|\_|", "", new_slug)
        if User.objects(slug=new_slug).count() > 0:
            i = 2
            new_slug = new_slug + "-%s" % i
            while User.objects(slug=new_slug).count() > 0:
                i += 1
                new_slug = re.sub(r"-([0-9])*$", "-%s" % i, new_slug)
        self.slug = new_slug

        if "googleusercontent.com" in self.image_url:
            self.image_url = re.sub(r"sz=([0-9]*)$", "sz=", self.image_url)

    def id_str(self):
        return str(self.id)

    def role(self):
        if self.can('admin'):
            return "Admin"
        if self.can('publish'):
            return "Publisher"
        if self.can('edit'):
            return "Editor"
        return "User"

    def __repr__(self):
        return 'User(id=%r, name=%r, email=%r, roles=%r, privileges=%r, gplus_id=%r, date_created=%r)' % \
            (self.id, self.name, self.email, self.roles,
             self.privileges, self.gplus_id, self.date_created)

    def __unicode__(self):
        if self.can('admin'):
            return '%r <%r> (Admin)' % (self.name, self.email)
        if self.can('publish'):
            return '%r <%r> (Publisher)' % (self.name, self.email)
        if self.can('edit'):
            return '%r <%r> (Editor)' % (self.name, self.email)
        else:
            return '%r <%r>' % (self.name, self.email)