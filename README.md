# Eventum

Eventum is a content management system for an event-driven blog that syncs with Google Calendar.

![Eventum](https://adicu.com/admin/media/uploads/home.png)

## Stack
- Built in [Flask][flask]
- [Flask-Mongoengine][flask-mongoengine] and [Mongoengine][mongoengine] are used to interface with [MongoDB][mongodb]  
- Authentication is done with [Google+ server-side flow][google-plus-server-side-flow]
- Forms and validation are done through [Flask-WTForms][flask-wtforms] and [WTForms][wtforms]
- CSS is generated from [SCSS][scss] and managed with [Flask-Assets][flask-assets]

## Usage

```
pip install eventum
```

## Local setup

Eventum runs on Linux and OSX.  To get it up an running, follow these steps:

1.  Install [MongoDB][mongodb] ([Ubuntu Linux][mongodb-linux], [OSX][mongodb-osx]).

    > On OSX, you may have to run `$ mkdir /data /data/db` before you can run `mongod` without errors.

2.  Authorize the Google Calendar API:

    **TODO**
    
    ```bash
    $ python -m eventum.authorize
    ```

5.  Install SASS gem `gem install sass`
    * otherwise, you will see an `OS` error

Then you should be all set to run!

## Developing

Here's how to run Eventum in a development environment:

```bash
mongod &
python setup.py devlelop
```

#### Developing without Authentication

It is possible to run Eventum without logging in using Google+ or authenticating with Google Calendar.  To do so, set the Flask configuration variable `EVENTUM_GOOGLE_AUTH_ENABLED` to `FALSE`:

```bash
# Whether or not to enable Google Auth or not.
echo $EVENTUM_GOOGLE_AUTH_ENABLED
```

## Organization / Structure

```bash
.
├── docs             # Builds our Sphinx documentation
├── eventum          # The Eventum module
│   ├── forms        # Flask-WTForms models, used for generating forms in HTML
│   │                #     and validating input
│   ├── lib          # Misc helpers, tasks, and modular libraries
│   ├── models       # Mongoengine Models
│   ├── routes       # All Flask routes, using Blueprints
│   ├── static
│   │   ├── css      # CSS
│   │   │   └── lib  # CSS libraries
│   │   ├── img      # Images
│   │   ├── js       # Javascript files
│   │   └── eventum_scss    # Stylesheets
│   ├── templates    # HTML templates
│   └── __init__.py  # All app-wide setup.  Called by `run.py`
└── Manifest.in      # Log Files
```

## Screenshots

![home](https://adicu.com/admin/media/uploads/home.png)
![editors](https://adicu.com/admin/media/uploads/editors.png)
![events](https://adicu.com/admin/media/uploads/events.png)

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
