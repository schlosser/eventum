from flask import make_response
import json

def response_from_json(data, code):
    text = data if type(data) == str else json.dumps(data)
    response = make_response(text, code)
    response.headers['Content-Type'] = 'application/json'
    return response


