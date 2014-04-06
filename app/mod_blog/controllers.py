from flask import Blueprint

mod_blog = Blueprint('blog', __name__, url_prefix='/blog')