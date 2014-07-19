from app import db
from datetime import datetime
now = datetime.now

class Whitelist(db.Document):
    """"""
    date_created = db.DateTimeField(required=True, default=now)
    date_modified = db.DateTimeField(required=True, default=now)
    email = db.EmailField(required=True, unique=True)
    user_type = db.StringField()
    redeemed = db.BooleanField(required=True, default=False)

    meta = { 'indexes': ['email'] }

    def clean(self):
        """Update date_modified and apply privileges shorthand notation."""
        self.date_modified = now()


    def __repr__(self):
        return 'Whitelist(email=%r, user_type=%r, redeemed=%r)' % (self.email, self.user_type, self.redeemed)

    def __unicode__(self):
        return 'Whitelist<%r>' % self.email
