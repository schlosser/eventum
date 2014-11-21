"""
.. module:: blog
    :synopsis: All routes on the ``blog`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask import Blueprint, render_template, abort, redirect, url_for

from app.models import BlogPost

blog = Blueprint('blog', __name__)

@blog.route('/blog', methods=['GET'])
def index():
    """View recent blog posts.

    **Route:** ``/blog``

    **Methods:** ``GET``
    """
    blog_posts = list(BlogPost.objects(published=True).order_by('-date_published')[:10])
    previous_index = None
    next_index = 1
    return render_template('blog/blog.html',
                           posts=blog_posts,
                           previous_index=previous_index,
                           next_index=next_index)

@blog.route('/blog/<int:index>', methods=['GET'])
def blog_archive(index):
    """View older blog posts.

    **Route:** ``/blog/<index>``

    **Methods:** ``GET``
    """
    index = int(index)

    if index <= 0:
        return redirect(url_for('.index'))


    blog_posts = BlogPost.objects(published=True).order_by('-date_published')
    if len(blog_posts) < 10*(index+1):
        next_index = None
    else:
        next_index = index + 1
    previous_index = index - 1
    return render_template('blog/blog.html',
                           posts=list(blog_posts[10*index:10*(index+1)]),
                           previous_index=previous_index,
                           next_index=next_index)

@blog.route('/blog/post/<slug>', methods=['GET'])
def post(slug):
    """View an individual blog post.

    **Route:** ``/blog/post/<slug>``

    **Methods:** ``GET``
    """
    if BlogPost.objects(slug=slug).count() != 1:
        abort(404)
    post = BlogPost.objects().get(slug=slug)

    recent_posts = BlogPost.objects(published=True,
                                    id__ne=post.id,
                                    featured_image__ne=None).order_by('-date_published')[:3]
    if not post.published:
        abort(404)
    return render_template('blog/post.html',
                           post=post,
                           recent_posts=recent_posts)