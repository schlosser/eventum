"""
.. module:: whitelist
    :synopsis: All routes on the ``whitelist`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import uuid

from flask import Blueprint, request, flash, redirect, url_for, current_app

from eventum.models import User, Whitelist, Image
from eventum.forms import AddToWhitelistForm
from eventum.lib.decorators import login_required
from eventum.routes.base import MESSAGE_FLASH, ERROR_FLASH

whitelist = Blueprint('whitelist', __name__)


@whitelist.route('/whitelist/delete/<email>', methods=['POST'])
@login_required
def delete(email):
    """Delete ``email`` from the whitelist.

    **Route:** ``/admin/whitelist/delete/<email>``

    **Methods:** ``POST``

    :param str email: The email address to delete from the whitelist.
    """
    if Whitelist.objects(email=email).count() > 0:
        Whitelist.objects.get(email=email).delete()
        flash("Whitelist entry revoked successfully.", MESSAGE_FLASH)
        return redirect(url_for('users.index'))
    flash('No such user in the database.', ERROR_FLASH)
    return redirect(url_for('users.index'))


@whitelist.route('/whitelist/add', methods=['POST'])
@login_required
def add():
    """Add and email to the whitelist.

    **Route:** ``/admin/whitelist/add``

    **Methods:** ``POST``
    """
    form = AddToWhitelistForm(request.form)

    if form.user_type.data == 'fake_user':
        if form.validate_on_submit():
            fake_id = str(uuid.uuid4())
            fake_email = fake_id[:10] + "@fake-users.com"
            filename = form.fake_user_image.data
            try:
                fake_image = Image.objects().get(filename=filename)
                fake_user = User(email=fake_email,
                                 gplus_id=fake_id,
                                 name=form.name.data,
                                 user_type=form.user_type.data,
                                 image=fake_image)
            except Image.DoesNotExist:
                fake_user = User(email=fake_email,
                                 gplus_id=fake_id,
                                 name=form.name.data,
                                 user_type=form.user_type.data)
            fake_user.save()
        else:
            current_app.logger.warning(form.errors)
    else:
        user_exists = User.objects(email=form.email.data).count() != 0
        if form.validate_on_submit() and not user_exists:
            wl = Whitelist(email=form.email.data,
                           user_type=form.user_type.data)
            wl.save()
        else:
            current_app.logger.warning(form.errors)
    return redirect(url_for('users.index'))
