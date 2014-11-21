from client import create_app as create_client_app
from eventum import create_app as create_eventum_app
from flask import url_for


def client_url_for(*args, **kwargs):
    client_app = create_client_app()
    ctx = client_app.test_request_context()
    ctx.push()
    kwargs['_external'] = True
    url = url_for(*args, **kwargs)
    ctx.pop()
    return url


def eventum_url_for(*args, **kwargs):
    eventum_app = create_eventum_app()
    ctx = eventum_app.test_request_context()
    ctx.push()
    kwargs['_external'] = True
    url = url_for(*args, **kwargs)
    ctx.pop()
    return url
