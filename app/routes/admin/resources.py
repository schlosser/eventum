from flask import Blueprint, render_template

resources = Blueprint('resources', __name__)

@resources.route('/resources')
def index():
	return render_template('admin/resources/index.html')

