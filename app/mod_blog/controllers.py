from app import app
from flask import Blueprint, render_template, request, send_from_directory
from app.mod_blog.models import BlogPost
from app.mod_blog.forms import CreateBlogPostForm

mod_blog = Blueprint('blog', __name__)

@mod_blog.route('/blog')
def blog():
	return render_template('blog/blog.html', posts=BlogPost.objects())

@mod_blog.route('/blog/posts')
def posts():
    return render_template('blog/posts.html', posts=BlogPost.objects())

@mod_blog.route('/blog/posts/edit', methods=['GET', 'POST'])
def create_post():
    form = CreateBlogPostForm(request.form)
    return render_template('blog/edit_post.html', form=form)

@mod_blog.route('/blog/posts/epiceditor/themes/<folder>/<path>')
def fetch_epiceditor_themes(folder, path):
    return send_from_directory(app.static_folder, "css/epiceditor/%s/%s" % (folder, path))