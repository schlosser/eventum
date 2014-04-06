from app.mod_auth.forms import LoginForm, AddUserForm, ChangePasswordForm
from app import mongo
from functools import wraps
from flask import Blueprint, render_template, request, flash, session, abort
from werkzeug import check_password_hash, generate_password_hash

mod_auth = Blueprint('auth', __name__)


@mod_auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = mongo.users.find_one({"email": form.email.data})
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Welcome, %s.' % (user.first_name))

    return render_template('auth/login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


@login_required
@mod_auth.route('/adduser', methods=['GET', 'POST'])
def add_user():
    # TODO: use the next variable if user was redirected to login
    form = AddUserForm(request.form)
    if form.validate_on_submit():
        # Register a new user in the database
        new_user = form.user_type(form.first_name.data,
                                  form.last_name.data,
                                  form.email.data,
                                  generate_password_hash(form.password.data))
        mongo.users.insert(new_user)
        flash('New %s added successfully.' %
              form.user_type.__class__.__name__.lower())
    return render_template('auth/add_user.html')


@mod_auth.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        if check_password_hash(session.user.password, form.old_password.data):
            user = mongo.users.find_one({"_id": session.user._id})
            user.password = generate_password_hash(form.password.data)
            mongo.users.save()
            flash('Password changed successfully')
        else:
            flash('Old Password is incorrect.', 'error-message')
    return render_template('auth/change_password.html')
