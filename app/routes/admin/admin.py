from app.lib.decorators import login_required
from flask import Blueprint, render_template, redirect, url_for

admin = Blueprint('admin', __name__)

@admin.route('/home')
@login_required
def index():
    return render_template("admin/admin.html")


@admin.route('/')
@login_required
def landing():
    return redirect(url_for('auth.login'))