from flask import Blueprint, render_template, request
from app.mod_blog.models import BlogPost
from app.mod_blog.forms import CreateBlogPostForm

mod_blog = Blueprint('blog', __name__)

@mod_blog.route('/blog')
def blog():
	return render_template('blog/blog.html', posts=BlogPost.objects())

@mod_blog.route('/blog/posts')
def posts():
    return render_template('blog/posts.html', posts=BlogPost.objects())

@mod_blog.route('/blog/posts/create', methods=['GET', 'POST'])
def create_post():
    form = CreateBlogPostForm(request.form)
    return render_template('blog/create_post.html', form=form)
