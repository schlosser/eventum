from flask import make_response
import json

def json_response(data, code):
    """Return a :class:`flask.Response` object ``data`` in the body, JSON
    encoding it if necessary.

    :param data: The data to be put in the response body.
    :type data: str or dict
    :param int code: The HTTP status code for the response.

    :returns: the response object
    :rtype: :class:`flask.Response`
    """
    # TODO: Split this out into two functions, one that take strings, and
    # another that takes dictionaries
    text = data if type(data) == str else json.dumps(data)
    response = make_response(text, code)
    response.headers['Content-Type'] = 'application/json'
    return response
