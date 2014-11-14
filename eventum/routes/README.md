# `/app/routes`

[Flask][flask] routes live here, organized into blueprints.  

[Blueprints][blueprints] allow namespacing of routes.  Each `.py` file here is a blueprint (except `base.py`), and contains routes that represent a part of the application.  For example, `blog.py` has routes for the user-facing blog, and `admin/posts.py` has routes for managing posts in the admin interface.

## Subdirectories

- `admin`: All blueprints for the admin interface

## Notable files

- `base.py` Any global Flask configurations, including
    + `@app.before_request`
    + `@app.after_request`
    + `@app.error_handler`
    + `@app.context_processor`

[blueprints]: http://flask.pocoo.org/docs/blueprints/
[flask]: http://flask.pocoo.org/
