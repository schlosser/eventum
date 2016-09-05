import pytest
from flask import Flask

from eventum import Eventum


@pytest.yield_fixture(scope="session")
def eventum(tmpdir_factory):
    app = Flask("testing")
    app.config["EVENTUM_SETTINGS"] = {
        "UPLOAD_FOLDER": str(tmpdir_factory.mktemp("upload")),
        "DELETE_FOLDER": str(tmpdir_factory.mktemp("delete")),
        "GOOGLE_AUTH_ENABLED": False,
    }
    app.config["SECRET_KEY"] = "HELLO"
    eventum = Eventum(app)

    with eventum.app.app_context():
        yield eventum
