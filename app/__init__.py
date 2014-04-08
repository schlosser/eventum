from flask import Flask, render_template, request
from flask.ext.openid import OpenID
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)
oid = OpenID(app, safe_roots=[])


def register_blueprints(app):
	from app.mod_auth.controllers import mod_auth as auth_module
	from app.mod_learn.controllers import mod_learn as learn_module
	from app.mod_events.controllers import mod_events as events_module
	from app.mod_blog.controllers import mod_blog as blog_module

	app.register_blueprint(auth_module)
	app.register_blueprint(learn_module)
	app.register_blueprint(events_module)
	app.register_blueprint(blog_module)

register_blueprints(app)

from app.mod_auth.decorators import login_required

@app.errorhandler(404)
def not_found(error):
	return render_template('error/404.html'), 404

@app.errorhandler(401)
def not_authorized(error):
	return render_template('error/401.html'), 401

@app.errorhandler(405)
def method_not_allowed(error):
	return render_template('error/405.html', method=request.method), 405

@app.route('/')
@login_required
def index():
	return render_template("app.html")
