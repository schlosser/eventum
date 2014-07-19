from app.models import User, Whitelist
from app.forms import AddToWhitelistForm, EditUserForm
from app.lib.decorators import login_required, development_only
from apiclient.discovery import build
from flask import Blueprint, render_template, request, \
    flash, session, g, redirect, url_for, abort
from bson import ObjectId

users = Blueprint('users', __name__)

gplus_service = build('plus', 'v1')

@users.route('/users', methods=['GET'])
@login_required
def index():
    """View and manage users

    Whitelisted users are the only ones allowed to make user accounts.
    """
    whitelist_form = AddToWhitelistForm()
    return render_template('admin/users/users.html',
                           whitelist_form=whitelist_form,
                           whitelist=Whitelist.objects(),
                           users=User.objects(),
                           current_user=g.user)

@users.route('/users/delete/<user_id>', methods=['POST'])
@login_required
def delete(user_id):
    """Delete the user with id `user_id`

    If the `revoke` property is set to true,
    then the user will be removed from the whitelist, and not be
    allowed to make an account again.
    """
    object_id = ObjectId(user_id)
    if User.objects(id=object_id).count() != 1:
        abort(401)
    user = User.objects().get(id=object_id)

    # Update whitelist
    wl = Whitelist.objects().get(email=user.email)
    wl.redeemed = False
    wl.save()
    user.delete()

    # Log out if a user is attempting to delete themselves
    if 'gplus_id' in session and user.gplus_id == session['gplus_id']:
        flash('You deleted yourself successfully. Logging out.')
        return redirect(url_for('.logout'), 303)
    flash('User deleted successfully.')

    return redirect(url_for('.index'), code=303)

@users.route('/user/<slug>', methods=['GET', 'POST'])
@login_required
def user(slug):
    """"""
    if User.objects(slug=slug).count() != 1:
        flash("Invalid user slug '%s'" % slug)
        abort(500)
    user = User.objects().get(slug=slug)
    form = EditUserForm(request.form,
                        name=user.name,
                        email=user.email,
                        # image_url=user.get_profile_picture(),
                        user_type=user.user_type)
    if request.method == 'POST':
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.user_type = form.user_type.data
            # user.image_url = form.image_url.data
            user.save()
            return redirect(url_for('.index'))
        else:
            flash("Your Form had errors: %s" % (form.errors))

    return render_template('admin/users/user.html', user=user, form=form,
                           current_user=g.user)

#============================================================
# Development Only (quick and dirty ways to play with Users)
#============================================================
@users.route('/become/<level>')
@development_only
@login_required
def become(level=0):
    """Change the privileges of the logged in user.

    level -- 1: Editor, 2: Publisher, 3: Admin
    """
    level = int(level)
    admin_privileges = {
        "edit": level > 0,
        "publish": level > 1,
        "admin": level > 2
    }
    db_dict = dict((("set__privileges__%s" % k, v)
                   for k, v in admin_privileges.iteritems()))
    User.objects(gplus_id=session['gplus_id']).update(**db_dict)
    return redirect(url_for('.index'))

@users.route('/super')
@development_only
@login_required
def super():
    """Special case of become()"""
    return redirect(url_for('.become', level=3))

@users.route('/view-users')
@development_only
def view():
    """Print out all the users"""
    return str(User.objects)

@users.route('/users/wipe', methods=['GET', 'POST'])
@development_only
def wipe():
    """Wipe all users from the database"""
    if request.method == "POST":
        for u in User.objects():
            u.delete()
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('.index'), code=303)
    return '''<form action="" method=post>
        <input type=submit value="Wipe the Database">
        </form>'''

@users.route('/session')
@development_only
def show_session():
    return "<p>" + str(dict(session)) + "</p>"
