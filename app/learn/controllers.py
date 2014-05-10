from flask import Blueprint, render_template

learn = Blueprint('learn', __name__, url_prefix='/learn')

@learn.route('/')
def index():
	return render_template('learn/index.html')

