from flask import make_response
import json

def response_from_json(string, code):
	response = make_response(json.dumps(string), code)
	response.headers['Content-Type'] = 'application/json'
	return response


