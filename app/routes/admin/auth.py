import string
import random
import httplib2
from app import app
from app.lib.networking import response_from_json
from app.models import User, Whitelist
from app.forms import CreateProfileForm
from app.lib.decorators import development_only
from apiclient.discovery import build
from flask import Blueprint, render_template, request, \
    flash, session, g, redirect, url_for
from oauth2client.client import (FlowExchangeError,
                                 flow_from_clientsecrets,
                                 AccessTokenCredentials)

auth = Blueprint('auth', __name__)

gplus_service = build('plus', 'v1')

@auth.route('/login', methods=['GET'])
def login():
    """If the user is not logged in, display an option to log in.  On click,
    make a request to Google to authenticate.

    If they are logged in, redirect.
    """
    if g.user is not None and 'gplus_id' in session:
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('admin.index'), code=303)
    load_csrf_token_into_session()
    args_next = request.args.get('next')
    next = args_next if args_next else request.url_root
    return render_template('admin/auth/login.html',
                           client_id=app.config["GOOGLE_CLIENT_ID"],
                           state=session['state'],
                           # reauthorize=True,
                           next=next)

WHITELIST_CODE = 1

@auth.route('/store-token', methods=['POST'])
def store_token():
    """Do the oauth flow for Google plus sign in, storing the access token
    in the session, and redircting to create an account if appropriate.

    Because this method will be called from a $.ajax() request in JavaScript,
    we can't return redirect(), so instead this method returns the URL that
    the user should be redirected to, and the redirect happens in
    .. highlight:: javascript

        success: function(response) {
            window.location.href = response;
        }
    """
    if request.args.get('state', '') != session.get('state'):
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
            return response_from_json({
                'code': WHITELIST_CODE,
                'title': 'User has not been whitelisted.',
                'email': email
                }, 401)

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
        return redirect(url_for('admin.index'), code=303)
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

    return render_template('admin/auth/create_profile.html',
                           image_url=request.args.get('image_url'), form=form)



@auth.route('/logout', methods=['GET'])
def logout():
    """Log the user out."""
    session.pop('gplus_id', None)
    g.user = None
    return redirect(url_for('client.index'))


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

    session.pop('gplus_id', None)
    g.user = None

    if result['status'] == '200':
        # Reset the user's session.
        del session['credentials']

        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('.login'), code=303)
    else:
        # For whatever reason, the given token was invalid.
        return response_from_json('Failed to revoke token for given user.',
                                  400)

@auth.route('/session')
@development_only
def view_session():
    return "<p>" + str(dict(session)) + "</p>"
