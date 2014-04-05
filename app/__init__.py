from flask import Flask, render_template, redirect, url_for
from bson.json_util import dumps
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
app.config.from_object('config')
mongo = PyMongo(app)

@app.route('/')
def home():
	return render_template("app.html")
