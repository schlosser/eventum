# `/app`

All code relevant to running Eventum lives here.

## Subdirectories

- `forms`: [Flask-WTForms][flask-wtforms] models, used for generating forms in HTML and validating input
- `lib`: Misc helpers, tasks, and modular libraries
- `models`: The [Mongoengine][mongoengine] models
- `routes`: The Flask Blueprints that handle routing
- `static`: CSS, JS, and images
- `templates`: HTML templates

## Notable files

- `__init__.py`: Holds all the setup and initialization of dependencies, Blueprints, and the database.


[mongoengine]: http://docs.mongoengine.org/
[flask-wtforms]: https://flask-wtf.readthedocs.org/en/latest/
