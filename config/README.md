# `/config`

Configuration and settings files live here.

## Notable files

- `flask_config.py`: Stores configurations for Flask, including secret keys, global variables, flags, and extenral integration account info.
- `requirements.txt`: Pip requirements.  Install from the root directory using:
  
    ```bash
    $ pip install -r config/requirements.txt --allow-external PIL --allow-  unverified 
    ```
- `scss.json`: Configuration for [Flask-Assets][flask-assets].  These configurations are loaded by `app/__init__.py` and used to compile SCSS files and generate the files in `/app/static/css/gen`.

[flask-assets]: http://flask-assets.readthedocs.org/en/latest/
