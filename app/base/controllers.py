from flask import Blueprint, render_template

base = Blueprint('base', __name__)
from app.auth.decorators import login_required

@base.route('/')
@login_required
def index():
	return render_template("app.html")