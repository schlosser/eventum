from flask import make_response
import json

def response_from_json(dictionary, code):
    response = make_response(json.dumps(dictionary), code)
    response.headers['Content-Type'] = 'application/json'
    return response


