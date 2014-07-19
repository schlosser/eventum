from flask.ext.wtf import Form
from wtforms import BooleanField

class DeleteEventForm(Form):

    delete_all = BooleanField('Delete All', default=False)
    delete_following = BooleanField('Delete Following', default=False)