Quickstart
==========

Eventum is a content management system for an event-driven blog that
syncs with Google Calendar.

Stack
-----

-  Built in `Flask <http://flask.pocoo.org/>`__
-  `Flask-Mongoengine <http://flask-mongoengine.readthedocs.org/en/latest/>`__
   and `Mongoengine <http://docs.mongoengine.org/>`__ are used to
   interface with `MongoDB <https://www.mongodb.org/>`__
-  Authentication is done with `Google+ server-side
   flow <https://developers.google.com/+/web/signin/server-side-flow>`__
-  Forms and validation are done through
   `Flask-WTForms <https://flask-wtf.readthedocs.org/en/latest/>`__ and
   `WTForms <http://wtforms.readthedocs.org/en/latest/>`__
-  CSS is generated from `SCSS <http://sass-lang.com/>`__ and managed
   with
   `Flask-Assets <http://flask-assets.readthedocs.org/en/latest/>`__

Setup
-----

Eventum runs on Linux and OSX. To get it up an running, follow these
steps:

1. Install `MongoDB <https://www.mongodb.org/>`__ (`Ubuntu
   Linux <http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/>`__,
   `OSX <http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/#install-mongodb-with-homebrew>`__).

   On OSX, you may have to run::

       $ mkdir /data /data/db

   before you can run ``mongod`` without errors.

2. Install
   `VirtualEnv <http://virtualenv.readthedocs.org/en/latest/>`__::

       $ sudo pip install virtualenv

3. Download a copy of ``client_secrets.json`` from the `Google Developer
   Console <https://console.developers.google.com/project/apps~adicu-com/apiui/credential>`__
   or from a friend, and place it in the ``config`` folder.

4. Authorize the Google Calendar API::

       $ python manage.py --authorize

Then you should be all set to run!

Developing
----------

Here's how to run Eventum in a development environment:

.. code:: bash

    mongod &
    virtualenv --no-site-packages .
    source bin/activate
    source config/settings.sh
    pip install -r config/requirements.txt

    python run.py

Or alternately:

.. code:: bash

    ./develop.sh
    source bin/activate
    source config/settings.sh
    python run.py

Developing without Authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to run Eventum without logging in using Google+ or
authenticating with Google Calendar. To do so, edit
``config/settings.sh`` and set ``GOOGLE_AUTH_ENABLED`` to ``FALSE``:

.. code:: bash

    # Whether or not to enable Google Auth or not.
    echo $GOOGLE_AUTH_ENABLED

Documentation
-------------

Eventum uses `Sphinx <http://sphinx-doc.org/>`__ to compile
documentation to an HTML website. This documentation is generated from
the source code.

Here's how to compile the docs:

.. code:: bash

    # The documentation requires that the app is runnable, so you must be in a
    # development environment
    ./develop.sh
    source bin/activate
    source config/settings.sh

    cd docs
    # This will generate the documentation website in /docs/_build/html
    make html

    # Then either host the docs on localhost:8000
    cd _build/html
    python -m SimpleHTTPServer .

    # Or open them directly
    open _build/html/index.html

Testing
-------

Tests live in the ``test`` directory, and can be run via nosetests:

.. code:: bash

    source bin/activate # If you are not already in your virtualenv
    nosetests

Organization / Structure
------------------------

.. code:: bash

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

