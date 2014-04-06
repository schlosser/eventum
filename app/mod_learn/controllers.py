from flask import Blueprint, render_template

mod_learn = Blueprint('learn', __name__, url_prefix='/learn')

@mod_learn.route('/')
def index():
	return render_template('learn/index.html')

