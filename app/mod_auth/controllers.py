from app import oid
from app.mod_auth.models import User
from app.mod_auth.forms import CreateProfileForm, AddUserForm
from mongoengine.queryset import DoesNotExist
from flask import Blueprint, render_template, request, flash, session, g, \
    redirect, url_for

mod_auth = Blueprint('auth', __name__)

GOOGLE_OPEN_ID_URL = "https://www.google.com/accounts/o8/id"


@mod_auth.before_request
def lookup_current_user():
    g.user = None
    if 'openid' in session:
        openid = session['openid']
        try:
            g.user = User.objects.get(openid=openid)
        except DoesNotExist:
            pass

from app.mod_auth.decorators import login_required


@mod_auth.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and 'openid' in session:
        return redirect(oid.get_next_url(), code=303)
    if request.method == 'POST':
        return oid.try_login(GOOGLE_OPEN_ID_URL,
                             ask_for=['email', 'nickname', 'image'],
                             ask_for_optional=['fullname'])
    return render_template('auth/login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    try:
        user = User.objects.get(openid=resp.identity_url)
        if user is not None:
            flash('Successfully signed in')
            g.user = user
            return redirect(oid.get_next_url(), code=303)
    except DoesNotExist:
        pass
    return redirect(url_for('.create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))


@mod_auth.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    form = CreateProfileForm(request.form,
                             name=request.args['name'],
                             email=request.args['email'])
    if form.validate_on_submit():
        new_user = User(openid=session['openid'],
                        name=form.name.data,
                        email=form.email.data)
        new_user.save()
        flash('Account created successfully.')
        return redirect(oid.get_next_url(), code=303)
    return render_template('auth/create_profile.html', form=form, next=oid.get_next_url())


@mod_auth.route('/logout')
def logout():
    session.pop('openid', None)
    g.user = None
    flash(u'You were signed out')
    return redirect(oid.get_next_url(), code=303)


@mod_auth.route('/super')
@login_required
def super():
    return redirect(url_for('.become', level=3))


@mod_auth.route('/become/<level>')
@login_required
def become(level=0):
    level = int(level)
    admin_privelages = {
        "edit": level>0,
        "publish": level>1,
        "admin": level>2
    }
    db_dict = dict((("set__privelages__%s" % k, v)
                   for k, v in admin_privelages.iteritems()))
    User.objects(openid=session['openid']).update(**db_dict)
    return redirect(url_for('.view_users'))


@mod_auth.route('/wipe')
@login_required
def wipe():
    User.objects.delete()
    return redirect(url_for('.view_users'))


@mod_auth.route('/adduser', methods=['GET', 'POST'])
@login_required
def add_user():
    # TODO: use the next variable if user was redirected to login
    form = AddUserForm(request.form)
    if form.validate_on_submit():
        # Register a new user in the database
        new_user = User(name="CHANGE ME", email=form.email.data)
        new_user.save()
    return render_template('auth/add_user.html')


@mod_auth.route('/view-users')
def view_users():
    return str(User.objects)


# @mod_auth.route('/changepassword', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     form = ChangePasswordForm(request.form)
#     if form.validate_on_submit():
#         if check_password_hash(session.user.password, form.old_password.data):
#             user = User.objects.get({"_id": session.user._id})
#             user.password = generate_password_hash(form.password.data)
#             user.save()
#             flash('Password changed successfully')
#         else:
#             flash('Old Password is incorrect.', 'error-message')
#     return render_template('auth/change_password.html')
