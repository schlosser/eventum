import string
import random
import httplib2
from app import app
from app.networking.responses import response_from_json
from app.auth.models import User, Whitelist
from app.auth.forms import CreateProfileForm, AddToWhitelistForm, EditUserForm
from apiclient.discovery import build
from mongoengine.queryset import DoesNotExist
from flask import Blueprint, render_template, request, \
    flash, session, g, redirect, url_for, abort
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets, \
    AccessTokenRefreshError, AccessTokenCredentials
from bson.objectid import ObjectId

auth = Blueprint('auth', __name__)

gplus_service = build('plus', 'v1')


@auth.before_request
def lookup_current_user():
    """Set the g.user variable to the User in the database that shares
    openid with the session, if one exists.

    Note that it gets called before all requests, but not before decorators.
    """
    g.user = None
    if 'gplus_id' in session:
        gplus_id = session['gplus_id']
        try:
            g.user = User.objects().get(gplus_id=gplus_id)
        except DoesNotExist:
            pass  # Fail gracefully if the user is not in the database yet


# We have to import the login_required decorator below
# lookup_current_user() to avoid circular dependency
from app.auth.decorators import login_required, development_only


@auth.route('/login', methods=['GET'])
def login():
    """If the user is not logged in, display an option to log in.  On click,
    make a request to Google to authenticate.

    If they are logged in, redirect.
    """
    if g.user is not None and 'gplus_id' in session:
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('base.index'), code=303)
    load_csrf_token_into_session()
    args_next = request.args.get('next')
    next = args_next if args_next else request.url_root
    return render_template('auth/login.html',
                           client_id=app.config["CLIENT_ID"],
                           state=session['state'],
                           # reauthorize=True,
                           next=next)


@auth.route('/store-token', methods=['POST'])
def store_token():
    """Do the oauth flow for Google plus sign in, storing the access token
    in the session, and redircting to create an account if appropriate.

    Because this method will be called from a $.ajax() request in JavaScript,
    we can't return redirect(), so instead this method returns the URL that
    the user should be redirected to, and the redirect happens in JavaScript:
        success: function(response) {
            window.location.href = response;
        }
    """
    if request.args.get('state', '') != session['state']:
        return response_from_json('Invalid state parameter.', 401)

    del session['state']
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'config/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return response_from_json('Failed to upgrade the authorization code.',
                                  401)

    gplus_id = credentials.id_token['sub']

    # Store the access token in the session for later use.
    session['credentials'] = credentials.access_token
    session['gplus_id'] = gplus_id

    if User.objects(gplus_id=gplus_id).count() == 0:
        # A new user model must be made

        # Get the user's name and email to populate the form
        http = httplib2.Http()
        http = credentials.authorize(http)
        people_document = gplus_service.people().get(
            userId='me').execute(http=http)

        # The user must be whitelisted in order to create an account.
        email = people_document['emails'][0]['value']
        if Whitelist.objects(email=email).count() != 1:
            return response_from_json('User has not been whitelisted.', 401)

        return response_from_json(url_for(
            '.create_profile',
            next=request.args.get('next'),
            name=people_document['displayName'],
            email=email,
            image_url=people_document['image']['url']), 200)

    user = User.objects().get(gplus_id=gplus_id)
    user.register_login()
    user.save()

    # The user already exists.  Redirect to the next url or
    # the root of the application ('/')
    if request.args.get('next'):
        return response_from_json(request.args.get('next'), 200)
    return response_from_json(request.url_root, 200)


@auth.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """Create a profile (filling in the form with openid data), and
    register it in the database.
    """
    if g.user is not None and 'gplus_id' in session:
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('base.index'), code=303)
    form = CreateProfileForm(request.form,
                             name=request.args['name'],
                             email=request.args['email'],
                             next=request.args['next'])
    if form.validate_on_submit():
        if User.objects(email=form.email.data).count() != 0:
            # A user with this email already exists.  Override it.
            user = User.objects.get(email=form.email.data)
            user.openid = session['openid']
            user.name = form.name.data
            flash('Account with this email already exists.  Overridden.')
            user.register_login()
            user.save()
        else:
            # Retreive their user type from the whitelist then remove them.
            wl = Whitelist.objects().get(email=form.email.data)
            user_type = wl.user_type
            wl.redeemed = True
            wl.save()
            # Create a brand new user
            user = User(email=form.email.data,
                        name=form.name.data,
                        gplus_id=session['gplus_id'],
                        user_type=user_type,
                        image_url=request.args.get('image_url'))
            flash('Account created successfully.')
            user.register_login()
            user.save()

        # redirect to the next url or the root of the application ('/')
        if form.next.data:
            # use code=303 to avoid POSTing to the next page.
            return redirect(form.next.data, code=303)
        # use code=303 to avoid POSTing to the next page.
        return redirect('/', code=303)

    return render_template('auth/create_profile.html',
                           image_url=request.args.get('image_url'), form=form)


@auth.route('/remove/<user_email>', methods=['GET'])
@login_required
def remove(user_email):
    """Remove the user with the specified email from the database.  If
    attempting to remove user that is currently logged in, do so and then
    log out.
    """
    user = User.objects.get(email=user_email)
    if user.gplus_id == session['gplus_id']:
        user.delete()
        return redirect(url_for('.logout'))
    user.delete()
    return redirect(url_for('.view_users'))


@auth.route('/logout', methods=['GET'])
def logout():
    """Log the user out."""
    session.pop('gplus_id', None)
    g.user = None
    flash(u'You were signed out')
    return redirect('http://adicu.com')


def load_csrf_token_into_session():
    """Create a unique session cross-site request forgery (CSRF) token and
    load it into the session for later verification.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state


@auth.route('/disconnect', methods=['GET', 'POST'])
def disconnect():
    """Revoke current user's token and reset their session."""
    # Only disconnect a connected user.
    credentials = AccessTokenCredentials(
        session.get('credentials'), request.headers.get('User-Agent'))
    if credentials is None:
        return response_from_json('Current user not connected.', 401)

    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        str(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del session['credentials']

        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('base.index'), code=303)
    else:
        # For whatever reason, the given token was invalid.
        return response_from_json('Failed to revoke token for given user.',
                                  400)


@auth.route('/people', methods=['GET'])
def people():
    """Get list of people user has shared with this app."""
    credentials = AccessTokenCredentials(
        session.get('credentials'), request.headers.get('User-Agent'))
    # Only fetch a list of people for connected users.
    if credentials is None:
        return response_from_json('Current user not connected.', 401)
    try:
        # Create a new authorized API client.
        http = httplib2.Http()
        http = credentials.authorize(http)
        # Get a list of people that this user has shared with this app.
        google_request = gplus_service.people().list(
            userId='me', collection='visible')
        result = google_request.execute(http=http)

        return response_from_json(result, 200)
    except AccessTokenRefreshError:
        return response_from_json('Failed to refresh access token.', 500)


@auth.route('/users', methods=['GET'])
@login_required
def users():
    """View and manage users

    Whitelisted users are the only ones allowed to make user accounts.
    """
    whitelist_form = AddToWhitelistForm()
    return render_template('auth/users.html',
                           whitelist_form=whitelist_form,
                           whitelist=Whitelist.objects(),
                           users=User.objects(),
                           current_user=g.user)


@auth.route('/user/<slug>', methods=['GET', 'POST'])
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
            return redirect(url_for('.users'))
        else:
            flash("Your Form had errors: %s" % (form.errors))

    return render_template('auth/user.html', user=user, form=form)


@auth.route('/users/delete/<user_id>', methods=['POST'])
@login_required
def users_delete(user_id):
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

    return redirect(url_for('.users'), code=303)

@auth.route('/whitelist/delete/<email>', methods=['POST'])
@login_required
def whitelist_delete(email):
    """Delete `email` from the whitelist."""
    if Whitelist.objects(email=email).count() > 0:
        Whitelist.objects.get(email=email).delete()
        flash("Whitelist entry revoked successfully.")
        return redirect(url_for('.users'))
    flash('No such user in the database.')
    return redirect(url_for('.users'))


@auth.route('/whitelist/add', methods=['POST'])
@login_required
def whitelist_add():
    """Add `email` to the whitelist."""
    form = AddToWhitelistForm(request.form)
    user_exists = User.objects(email=form.email.data).count() != 0
    if form.validate_on_submit() and not user_exists:
        wl = Whitelist(email=form.email.data, user_type=form.user_type.data)
        wl.save()
    else:
        # print form.errors
        pass
    return redirect(url_for('.users'))


#============================================================
# Development Only (quick and dirty ways to play with Users)
#============================================================
@auth.route('/become/<level>')
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
    return redirect(url_for('.view_users'))


@auth.route('/super')
@development_only
@login_required
def super():
    """Special case of become()"""
    return redirect(url_for('.become', level=3))


@auth.route('/view-users')
@development_only
def view_users():
    """Print out all the users"""
    return str(User.objects)


@auth.route('/view-whitelist')
@development_only
def view_whitelist():
    """Print out all the users"""
    return str(Whitelist.objects)


@auth.route('/wipe', methods=['GET', 'POST'])
@development_only
def wipe():
    """Wipe all users from the database"""
    if request.method == "POST":
        for u in User.objects():
            u.delete()
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('.view_users'), code=303)
    return '''<form action="/wipe" method=post>
        <input type=submit value="Wipe the Database">
        </form>'''


@auth.route('/session')
@development_only
def view_session():
    return "<p>" + str(dict(session)) + "</p>"

@auth.route('/users/save')
def save_users():
    for user in User.objects():
        user.save()
    return "hi"
