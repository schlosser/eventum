from flask.ext.wtf import Form
from wtforms import TextField, HiddenField
from wtforms.validators import URL, Email, Required

EMAIL_ERROR = 'Please provide a valid email address.'

class CreateProfileForm(Form):
    name = TextField('Full Name')
    email = TextField('Email Address',
                      [Email(message=EMAIL_ERROR), Required(message=EMAIL_ERROR)])
    next = HiddenField('hidden', [URL(require_tld=False)])