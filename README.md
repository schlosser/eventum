# Eventum

Eventum is a content management system for an event-driven blog that syncs with Google Calendar.

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
pip install -r config/requirements.txt
python run.py
```
Or alternately:
```
./develop.sh
source bin/activate
python run.py
```

#### Developing without Authentication

Edit `config/flask_config.py` and set `AUTH` to `False`:
```diff

```

## Organization / Structure

```
.
├── app            # All code related to the running of the app
│   ├── forms      # Flask-WTForms models, used for generating forms in HTML
│   │              #     and validating input
│   ├── lib        # Misc helpers, tasks, and modular libraries
│   ├── models     # Mongoengine Models
│   ├── routes     # All Flask routes, using Blueprints
│   ├── static     
│   │   ├── css    # Compiled CSS 
│   │   ├── img    # Images
│   │   ├── js     # Javascript files
│   │   └── scss   # Stylesheets
│   └── templates  # HTML templates
├── config         # Configuration files
├── manage.py      # Run this with a `--authorize` flag to authenticate GCal
├── run.py         # Runs the app!
└── test           # Unit tests
```


[google-developer-console]: https://console.developers.google.com/project/apps~adicu-com/apiui/credential
[mongodb]: https://www.mongodb.org/
[mongodb-linux]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
[mongodb-osx]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/#install-mongodb-with-homebrew
[virtualenv]: http://virtualenv.readthedocs.org/en/latest/