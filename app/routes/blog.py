from flask import Blueprint, render_template, abort

from app.models import BlogPost

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def index():
    return render_template('blog/blog.html', posts=BlogPost.objects())

@blog.route('/blog/post/<slug>')
def post(slug):
    if BlogPost.objects(slug=slug).count() != 1:
        abort(404)
    post = BlogPost.objects().get(slug=slug)

    if not post.published:
        abort(404)
    return render_template('blog/post.html', post=post)

