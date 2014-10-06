# Eventum

Eventum is a content management system for an event-driven blog that syncs with Google Calendar.

## Stack
- Built in [Flask][flask]
- [Flask-Mongoengine][flask-mongoengine] and [Mongoengine][mongoengine] are used to interface with [MongoDB][mongodb]  
- Authentication is done with [Google+ server-side flow][google-plus-server-side-flow]
- Forms and validation are done through [Flask-WTForms][flask-wtforms] and [WTForms][wtforms]
- CSS is generated from [SCSS][scss] and managed with [Flask-Assets][flask-assets]

## Setup

Eventum runs on Linux and OSX.  To get it up an running, follow these steps:

1.  Install [MongoDB][mongodb] ([Ubuntu Linux][mongodb-linux], [OSX][mongodb-osx]).

    > On OSX, you may have to run `$ mkdir /data /data/db` before you can run `mongod` without errors.

2.  Install [VirtualEnv][virtualenv]:
    ```bash
    $ sudo pip install virtualenv
    ```

4.  Download a copy of `client_secrets.json` from the [Google Developer Console][google-developer-console] or from a friend, and place it in the `config` folder.

5.  Authorize the Google Calendar API:
    ```bash
    $ python manage.py --authorize
    ```

Then you should be all set to run!

## Developing

Here's how to run Eventum in a development environment:

```bash
mongod &
virtualenv --no-site-packages .
source bin/activate
source config/settings.sh
pip install -r config/requirements.txt

python run.py
```

Or alternately:

```
./develop.sh
source bin/activate
source config/settings.sh
python run.py
```

#### Developing without Authentication

It is possible to run Eventum without logging in using Google+ or authenticating with Google Calendar.  To do so, edit `config/settings.sh` and set `GOOGLE_AUTH_ENABLED` to `FALSE`:

```bash
# Whether or not to enable Google Auth or not.
echo $GOOGLE_AUTH_ENABLED
```

## Testing

Tests live in the `test` directory, and can be run via nosetests:

```bash
source bin/activate # If you are not already in your virtualenv
nosetests
```

## Organization / Structure

```bash
.
├── app              # All code related to the running of the app
│   ├── forms        # Flask-WTForms models, used for generating forms in HTML
│   │                #     and validating input
│   ├── lib          # Misc helpers, tasks, and modular libraries
│   ├── models       # Mongoengine Models
│   ├── routes       # All Flask routes, using Blueprints
│   ├── static
│   │   ├── css      # CSS
│   │   │   ├── lib  # CSS libraries
│   │   │   └── gen  # CSS generated from SCSS
│   │   ├── img      # Images
│   │   ├── js       # Javascript files
│   │   └── scss     # Stylesheets
│   ├── templates    # HTML templates
│   └── __init__.py  # All app-wide setup.  Called by `run.py`
├── config           # Configuration files
├── data             # Backup data
├── manage.py        # Various scripts.  Run `python manage.py` to view usage.
├── run.py           # Runs the app!
├── script           # Scripts run by `manage.py` outside of the app
└── test             # Unit tests
```

[flask]: http://flask.pocoo.org/
[flask-assets]: http://flask-assets.readthedocs.org/en/latest/
[flask-mongoengine]: http://flask-mongoengine.readthedocs.org/en/latest/
[flask-wtforms]: https://flask-wtf.readthedocs.org/en/latest/
[google-developer-console]: https://console.developers.google.com/project/apps~adicu-com/apiui/credential
[google-plus-server-side-flow]: https://developers.google.com/+/web/signin/server-side-flow
[mongodb]: https://www.mongodb.org/
[mongodb-linux]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
[mongodb-osx]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/#install-mongodb-with-homebrew
[mongoengine]: http://docs.mongoengine.org/
[scss]: http://sass-lang.com/
[virtualenv]: http://virtualenv.readthedocs.org/en/latest/
[wtforms]: http://wtforms.readthedocs.org/en/latest/
