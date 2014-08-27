from app.models import User, Whitelist, Image
from app.forms import AddToWhitelistForm
from app.lib.decorators import login_required, development_only
from flask import Blueprint, request, flash, redirect, url_for
import uuid

whitelist = Blueprint('whitelist', __name__)

@whitelist.route('/whitelist/delete/<email>', methods=['POST'])
@login_required
def delete(email):
    """Delete `email` from the whitelist."""
    if Whitelist.objects(email=email).count() > 0:
        Whitelist.objects.get(email=email).delete()
        flash("Whitelist entry revoked successfully.")
        return redirect(url_for('users.index'))
    flash('No such user in the database.')
    return redirect(url_for('users.index'))


@whitelist.route('/whitelist/add', methods=['POST'])
@login_required
def add():
    """Add `email` to the whitelist."""
    form = AddToWhitelistForm(request.form)

    if form.user_type.data == 'fake_user':
        if form.validate_on_submit():
            fake_id = str(uuid.uuid4())
            fake_email = fake_id[:10] + "@fake-users.com"
            filename = form.fake_user_image.data
            try:
                import ipdb; ipdb.set_trace()
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
            print form.errors
    else:
        user_exists = User.objects(email=form.email.data).count() != 0
        if form.validate_on_submit() and not user_exists:
            wl = Whitelist(email=form.email.data, user_type=form.user_type.data)
            wl.save()
        else:
            print form.errors
    return redirect(url_for('users.index'))

@whitelist.route('/whitelist/view')
@development_only
def view():
    """Print out all the users"""
    return str(Whitelist.objects)


@whitelist.route('/whitelist/wipe', methods=['GET', 'POST'])
@development_only
def wipe():
    """Wipe all users from the database"""
    if request.method == "POST":
        for w in Whitelist.objects():
            w.delete()
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('users.index'), code=303)
    return '''<form action="" method=post>
        <input type=submit value="Wipe the Database">
        </form>'''