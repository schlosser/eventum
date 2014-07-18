from flask import Blueprint, render_template, request

networking = Blueprint('networking', __name__)

@networking.errorhandler(404)
def not_found(error):
	return render_template('error/404.html'), 404

@networking.errorhandler(401)
def not_authorized(error):
	return render_template('error/401.html'), 401

@networking.errorhandler(405)
def method_not_allowed(error):
	return render_template('error/405.html', method=request.method), 405


from app import app
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response