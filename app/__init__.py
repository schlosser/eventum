from flask import Flask, render_template
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.config.from_object('config')
mongo = PyMongo(app)

from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_learn.controllers import mod_learn as learn_module
from app.mod_events.controllers import mod_events as events_module
from app.mod_blog.controllers import mod_blog as blog_module

app.register_blueprint(auth_module)
app.register_blueprint(learn_module)
app.register_blueprint(events_module)
app.register_blueprint(blog_module)

@app.errorhandler(404)
def not_found(error):
	return render_template('error/404.html'), 404

@app.route('/')
def home():
	return render_template("app.html")
