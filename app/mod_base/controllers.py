from flask import Blueprint, render_template

mod_base = Blueprint('base', __name__)
from app.mod_auth.decorators import login_required

@mod_base.route('/')
@login_required
def index():
	return render_template("app.html")