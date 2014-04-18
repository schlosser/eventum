from flask import Blueprint

mod_blog = Blueprint('blog', __name__, url_prefix='/blog')

@mod_blog.route('/')
def blog():
	return "blog"