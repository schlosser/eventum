from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)


def register_blueprints(app):
	"""Registers all the Blueprints (modules) in a function, to avoid circular
	dependancies
	"""
	from app.mod_auth.controllers import mod_auth as auth_module
	from app.mod_learn.controllers import mod_learn as learn_module
	from app.mod_events.controllers import mod_events as events_module
	from app.mod_blog.controllers import mod_blog as blog_module
	from app.mod_networking.controllers import mod_networking as networking_module

	app.register_blueprint(auth_module)
	app.register_blueprint(learn_module)
	app.register_blueprint(events_module)
	app.register_blueprint(blog_module)
	app.register_blueprint(networking_module)

register_blueprints(app)
# we can only import the login_required decorator after registering
# blueprints.
from app.mod_auth.decorators import login_required


@app.route('/')
@login_required
def index():
	return render_template("app.html")
