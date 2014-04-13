from flask import Blueprint, render_template, request

mod_networking = Blueprint('networking', __name__)

@mod_networking.errorhandler(404)
def not_found(error):
	return render_template('error/404.html'), 404

@mod_networking.errorhandler(401)
def not_authorized(error):
	return render_template('error/401.html'), 401

@mod_networking.errorhandler(405)
def method_not_allowed(error):
	return render_template('error/405.html', method=request.method), 405
