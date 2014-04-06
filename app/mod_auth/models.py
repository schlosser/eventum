from app.mod_base.models import DBItem
from datetime import datetime
now = datetime.now


class User(DBItem):

    DEFAULT_PRIVELAGES = {
        "edit": False,
        "publish": False,
        "admin": False
    }

    def __init__(self, first_name, last_name, email, password,
                 roles=[], privelages={}):
        """Create an instance of a Person

        Keyword Arguments:
        roles -- a list of positions that this person holds (ie. ["newsletter"])
        privelages -- overwrites DEFAULT_PRIVELAGES or adds new fields
        """
        self.first_name = first_name
        self.last_name = last_name
        self.name = "%s %s" % (first_name, last_name)
        self.email = email
        self.password = password
        self.roles = roles
        self.privelages = self.__class__.DEFAULT_PRIVELAGES.copy()
        self.privelages.update(privelages)
        self.last_logon = now()

    def can(self, privelage):
        return self.privelages.get(privelage)

    def __repr__(self):
        return '%r(name=%r, email=%r, roles=%r, privelages=%r)' % \
            (self.__class__.__name__, self.name,
             self.email, self.roles, self.privelages)

    def __unicode__(self):
        if self.__class__.__name__ != "Person":
            return '%r <%r> (%r)' % (self.name, self.email,
                                     self.__class__.__name__)
        else:
            return '%r <%r>' % (self.name, self.email)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Editor(User):

    DEFAULT_PRIVELAGES = {
        "edit": True,
        "publish": False,
        "admin": False
    }


class Publisher(User):

    DEFAULT_PRIVELAGES = {
        "edit": True,
        "publish": True,
        "admin": False
    }


class Admin(User):

    DEFAULT_PRIVELAGES = {
        "edit": True,
        "publish": True,
        "admin": True
    }
