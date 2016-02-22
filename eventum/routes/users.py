"""
.. module:: users
    :synopsis: All routes on the ``users`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from eventum.models import User, Whitelist, Image
from eventum.forms import AddToWhitelistForm, EditUserForm, UploadImageForm
from eventum.lib.decorators import login_required, development_only
from eventum.routes.base import MESSAGE_FLASH, ERROR_FLASH
from apiclient.discovery import build
from mongoengine import DoesNotExist
from flask import Blueprint, render_template, request, \
    flash, session, g, redirect, url_for, abort
from bson import ObjectId

users = Blueprint('users', __name__)

gplus_service = build('plus', 'v1')


@users.route('/users', methods=['GET'])
@login_required
def index():
    """View and manage users.

    Whitelisted users are the only ones allowed to make user accounts.

    **Route:** ``/admin/users``

    **Methods:** ``GET``
    """

    upload_form = UploadImageForm()
    whitelist_form = AddToWhitelistForm()
    return render_template('eventum_users/users.html',
                           whitelist_form=whitelist_form,
                           upload_form=upload_form,
                           whitelist=Whitelist.objects(redeemed=False),
                           users=User.objects(),
                           images=Image.objects(),
                           current_user=g.user)


@users.route('/users/me', methods=['GET'])
@login_required
def me():
    """View the current user's profile.

    **Route:** ``/admin/users/me``

    **Methods:** ``GET``
    """
    return redirect(url_for(".user", slug=g.user.slug))


@users.route('/users/delete/<user_id>', methods=['POST'])
@login_required
def delete(user_id):
    """Delete the user with id ``user_id``

    If the ``revoke`` property is set to true,
    then the user will be removed from the whitelist, and not be
    allowed to make an account again.

    **Route:** ``/admin/users/delete/<user_id>``

    **Methods:** ``POST``
    """
    object_id = ObjectId(user_id)
    if User.objects(id=object_id).count() != 1:
        abort(401)
    user = User.objects().get(id=object_id)

    # Update whitelist
    try:
        wl = Whitelist.objects().get(email=user.email)
        wl.redeemed = False
        wl.save()
    except DoesNotExist:
        pass
    user.delete()

    # Log out if a user is attempting to delete themselves
    if 'gplus_id' in session and user.gplus_id == session['gplus_id']:
        flash('You deleted yourself successfully. Logging out.', MESSAGE_FLASH)
        return redirect(url_for('.logout'), 303)
    flash('User deleted successfully.', MESSAGE_FLASH)

    return redirect(url_for('.index'), code=303)


@users.route('/user/<slug>', methods=['GET', 'POST'])
@login_required
def user(slug):
    """View and edit the profile of a user.

    **Route:** ``/admin/user/<slug>``

    **Methods:** ``GET, POST``
    """
    try:
        user = User.objects().get(slug=slug)
    except DoesNotExist:
        flash("Invalid user slug '{}'".format(slug), ERROR_FLASH)
        return redirect(url_for('.index'))

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
            flash("Your Form had errors: {}".format(form.errors), ERROR_FLASH)

    return render_template('eventum_users/user.html', user=user, form=form,
                           current_user=g.user)


# ============================================================
#  Development Only (quick and dirty ways to play with Users)
# ============================================================
@users.route('/become/<level>', methods=['GET'])
@development_only
@login_required
def become(level=0):
    """Change the privileges of the logged in user.

    **Route:** ``/admin/become``

    **Methods:** ``GET``

    :param int level: 1: Editor, 2: Publisher, 3: Admin
    """
    level = int(level)
    admin_privileges = {
        "edit": level > 0,
        "publish": level > 1,
        "admin": level > 2
    }
    db_dict = dict((("set__privileges__{}".format(k), v)
                   for k, v in admin_privileges.iteritems()))
    User.objects(gplus_id=session['gplus_id']).update(**db_dict)
    return redirect(url_for('.index'))


@users.route('/super', methods=['GET'])
@development_only
@login_required
def super():
    """Special case of :func:``become()`` for becoming an admin.

    **Route:** ``/admin/super``

    **Methods:** ``GET``
    """
    return redirect(url_for('.become', level=3))
