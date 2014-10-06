# `/config`

Configuration and settings files live here.

## Notable files

- `settings.sh`: Stores configurations for Flask, including secret keys, global variables, flags, and extenral integration account info.
- `flask_config.py`: This pulls in all configurations for Eventum that are stored in environment variables. A few configurations are constants and are stored here.
- `adi_config.py`: This stores some ADI-specific configurations for Eventume.
- `requirements.txt`: Pip requirements.  Install from the root directory using:

    ```bash
    $ pip install -r config/requirements.txt
    ```
- `scss.json`: Configuration for [Flask-Assets][flask-assets].  These configurations are loaded by `app/__init__.py` and used to compile SCSS files and generate the files in `/app/static/css/gen`.

[flask-assets]: http://flask-assets.readthedocs.org/en/latest/
