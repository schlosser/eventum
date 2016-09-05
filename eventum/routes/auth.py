"""
.. module:: auth
    :synopsis: All routes on the ``auth`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import base64
import httplib2
import os

from apiclient.discovery import build
from flask import (Blueprint, render_template, request, flash, session, g,
                   redirect, url_for, current_app)
from oauth2client.client import (FlowExchangeError,
                                 flow_from_clientsecrets,
                                 AccessTokenCredentials)

from eventum.lib.json_response import json_success, json_error_message
from eventum.models import User, Whitelist
from eventum.forms import CreateProfileForm
from eventum.routes.base import MESSAGE_FLASH

auth = Blueprint('auth', __name__)

gplus_service = build('plus', 'v1')


@auth.route('/login', methods=['GET'])
def login():
    """If the user is not logged in, display an option to log in.  On click,
    make a request to Google to authenticate.

    If they are logged in, redirect.

    **Route:** ``/admin/login``

    **Methods:** ``GET``
    """
    if g.user is not None and 'gplus_id' in session:
        # use code=303 to avoid POSTing to the next page.
        return redirect(url_for('admin.index'), code=303)
    load_csrf_token_into_session()
    args_next = request.args.get('next')
    next = args_next if args_next else request.url_root
    client_id = current_app.config['EVENTUM_GOOGLE_CLIENT_ID']
    return render_template('eventum_auth/login.html',
                           client_id=client_id,
                           state=session['state'],
                           # reauthorize=True,
                           next=next)


@auth.route('/store-token', methods=['POST'])
def store_token():
    """Do the oauth flow for Google plus sign in, storing the access token
    in the session, and redircting to create an account if appropriate.

    Because this method will be called from a ``$.ajax()`` request in
    JavaScript, we can't return ``redirect()``, so instead this method returns
    the URL that the user should be redirected to, and the redirect happens in
    html:

    .. code:: javascript

        success: function(response) {
            window.location.href = response.data.redirect_url;
        }

    **Route:** ``/admin/store-token``

    **Methods:** ``POST``
    """
    if request.args.get('state', '') != session.get('state'):
        return json_error_message('Invalid state parameter.', 401)

    del session['state']
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            current_app.config['EVENTUM_CLIENT_SECRETS_PATH'],
            scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return json_error_message('Failed to upgrade the authorization code.',
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
            return json_error_message('User has not been whitelisted.',
                                      401,
                                      {'whitelisted': False, 'email': email})

        return json_success({
            'redirect_url': url_for('.create_profile',
                                    next=request.args.get('next'),
                                    name=people_document['displayName'],
                                    email=email,
                                    image_url=people_document['image']['url'])
        })

    user = User.objects().get(gplus_id=gplus_id)
    user.register_login()
    user.save()

    # The user already exists.  Redirect to the next url or
    # the root of the application ('/')
    if request.args.get('next'):
        return json_success({'redirect_url': request.args.get('next')})
    return json_success({'redirect_url': request.url_root})


@auth.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """Create a profile (filling in the form with openid data), and
    register it in the database.

    **Route:** ``/admin/create-profile``

    **Methods:** ``GET, POST``
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
            flash('Account with this email already exists.  Overridden.',
                  MESSAGE_FLASH)
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
            flash('Account created successfully.', MESSAGE_FLASH)
            user.register_login()
            user.save()

        # redirect to the next url or the root of the application ('/')
        if form.next.data:
            # use code=303 to avoid POSTing to the next page.
            return redirect(form.next.data, code=303)
        # use code=303 to avoid POSTing to the next page.
        return redirect('/', code=303)

    return render_template('eventum_auth/create_profile.html',
                           image_url=request.args.get('image_url'), form=form)


@auth.route('/logout', methods=['GET'])
def logout():
    """Logs out the current user.

    **Route:** ``/admin/logout``

    **Methods:** ``GET``
    """
    session.pop('gplus_id', None)
    g.user = None
    return redirect(url_for('client.index'))


def load_csrf_token_into_session():
    """Create a unique session cross-site request forgery (CSRF) token and
    load it into the session for later verification.
    """
    # 24 bytes in b64 == 32 characters
    session['state'] = base64.urlsafe_b64encode(os.urandom(24))


@auth.route('/disconnect', methods=['GET', 'POST'])
def disconnect():
    """Revoke current user's token and reset their session.

    **Route:** ``/admin/disconnect``

    **Methods:** ``GET, POST``
    """
    # Only disconnect a connected user.
    credentials = AccessTokenCredentials(
        session.get('credentials'), request.headers.get('User-Agent'))
    if credentials is None:
        return json_error_message('Current user not connected.', 401)

    # Execute HTTP GET request to revoke current token.
    access_token = credentials.access_token
    url = ('https://accounts.google.com/o/oauth2/revoke?token={}'
           .format(str(access_token)))
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    session.pop('gplus_id', None)
    g.user = None

    if result['status'] == '200':
        # Reset the user's session.
        del session['credentials']

    else:
        # For whatever reason, the given token was invalid.
        current_app.logger.error('Failed to revoke token for given user.')

    # use code=303 to avoid POSTing to the next page.
    return redirect(url_for('.login'), code=303)
