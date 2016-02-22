from flask import Blueprint, current_app, send_from_directory

eventum = Blueprint('eventum', __name__)


@eventum.route('/static/<path:filename>', methods=['GET'])
def static(filename):
    return send_from_directory(current_app.config['EVENTUM_STATIC_FOLDER'],
                               filename)
