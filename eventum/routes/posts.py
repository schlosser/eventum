"""
.. module:: posts
    :synopsis: All routes on the ``posts`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from flask import Blueprint, render_template, request, send_from_directory, \
    abort, redirect, url_for, g, flash, current_app

from bson.objectid import ObjectId
from bson.objectid import InvalidId
from mongoengine.errors import DoesNotExist, ValidationError
from eventum.models import BlogPost, Image, User, Tag
from eventum.forms import CreateBlogPostForm, UploadImageForm
from eventum.lib.decorators import login_required, requires_privilege
from eventum.routes.base import MESSAGE_FLASH, ERROR_FLASH

posts = Blueprint('posts', __name__)


@posts.route('/posts', methods=['GET'])
@login_required
def index():
    """View all of the blog posts.

    **Route:** ``/admin/posts``

    **Methods:** ``GET``
    """
    all_posts = BlogPost.objects().order_by('published', '-date_published')
    return render_template('eventum_posts/posts.html', posts=all_posts)


@posts.route('/posts/new', methods=['GET', 'POST'])
@requires_privilege('edit')
def new():
    """Create a new blog post.

    **Route:** ``/admin/posts/new``

    **Methods:** ``POST``
    """
    form = CreateBlogPostForm(request.form)
    form.author.choices = [
        (str(u.id), u.name + " (You)" if u == g.user else u.name)
        for u in User.objects()
    ]
    form.author.data = str(g.user.id)
    upload_form = UploadImageForm()
    if form.validate_on_submit():
        author = User.objects().get(id=ObjectId(form.author.data))
        images = [Image.objects().get(filename=fn) for fn in form.images.data]
        tags = Tag.get_or_create_tags(form.tags.data)
        post = BlogPost(title=form.title.data,
                        slug=form.slug.data,
                        images=images,
                        markdown_content=form.body.data,
                        author=author,
                        posted_by=g.user, post_tags=tags)
        post.save()

        if form.published.data:
            post.publish()
        else:
            post.unpublish()

        if form.preview.data is True:
            return redirect(url_for('blog.preview', slug=post.slug))

        return redirect(url_for('.index'))
    images = Image.objects()
    return render_template('eventum_posts/edit.html', user=g.user, form=form,
                           images=images, upload_form=upload_form)


@posts.route('/posts/edit/<post_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit(post_id):
    """Edit an existing blog post.

    **Route:** ``/admin/posts/edit/<post_id>``

    **Methods:** ``GET, POST``

    :param str post_id: The ID of the post to edit.
    """
    try:
        object_id = ObjectId(post_id)
    except InvalidId:
        return abort(404)
    try:
        post = BlogPost.objects().with_id(object_id)
    except (DoesNotExist, ValidationError):
        flash('Cannot find blog post with id {}.'.format(post_id), ERROR_FLASH)
        return redirect(url_for('.index'))

    if request.method == 'POST':
        form = CreateBlogPostForm(request.form)
        form.author.choices = [
            (str(u.id), u.name + " (You)" if u == g.user else u.name)
            for u in User.objects()]
        form.author.default = str(g.user.id)

        if form.validate_on_submit():
            post.title = form.title.data
            post.author = User.objects.get(id=ObjectId(form.author.data))
            post.slug = form.slug.data
            post.markdown_content = form.body.data
            post.images = [
                Image.objects().get(filename=fn) for fn in form.images.data
            ]

            post.post_tags = Tag.get_or_create_tags(form.tags.data)
            if form.featured_image.data:
                post.featured_image = Image.objects().get(
                    filename=form.featured_image.data)
            else:
                post.featured_image = None
            post.save()

            if post.published != form.published.data:
                if form.published.data:
                    post.publish()
                    flash('Blogpost published', MESSAGE_FLASH)
                else:
                    post.unpublish()
                    flash('Blogpost unpublished', MESSAGE_FLASH)

            if form.preview.data is True:
                return redirect(url_for('blog.preview', slug=post.slug))

    upload_form = UploadImageForm()
    feat_img = post.featured_image.filename if post.featured_image else None
    form = CreateBlogPostForm(request.form,
                              title=post.title,
                              slug=post.slug,
                              published=post.published,
                              body=post.markdown_content,
                              images=[image.filename for image in post.images],
                              author=str(post.author.id),
                              featured_image=feat_img, tags=post.post_tags)
    form.author.choices = [
        (str(u.id), u.name + " (You)" if u == g.user else u.name)
        for u in User.objects()
    ]
    form.author.default = str(g.user.id)
    images = [image for image in Image.objects() if image not in post.images]

    return render_template('eventum_posts/edit.html',
                           user=g.user,
                           form=form,
                           post=post,
                           images=images,
                           upload_form=upload_form)


@posts.route('/posts/delete/<post_id>', methods=['POST'])
def delete(post_id):
    """Delete an existing blog post.

    **Route:** ``/admin/posts/delete/<post_id>``

    **Methods:** ``POST``

    :param str post_id: The ID of the post to edit.
    """
    object_id = ObjectId(post_id)
    if BlogPost.objects(id=object_id).count() == 1:
        post = BlogPost.objects().with_id(object_id)
        post.delete()
    else:
        flash('Invalid event id', ERROR_FLASH)
    return redirect(url_for('.index'))


@posts.route('/posts/edit/epiceditor/themes/<folder>/<path>', methods=['GET'])
@posts.route('/posts/epiceditor/themes/<folder>/<path>', methods=['GET'])
@posts.route('/events/edit/epiceditor/themes/<folder>/<path>', methods=['GET'])
@posts.route('/events/epiceditor/themes/<folder>/<path>', methods=['GET'])
@login_required
def fetch_epiceditor_themes(folder, path):
    """Static path for the css files for Epiceditor. Because there doesn't
    appear to be a way to customize the URL at which EpicEditor requests it's
    static files, there isn't any way to serve them except by putting them at'
    all of the different places where EpicEditor might look (depending on what
    page it is on when it requests static files).

    **Route:** ``/posts/edit/epiceditor/themes/<folder>/<path>``

    **Route:** ``/posts/epiceditor/themes/<folder>/<path>``

    **Route:** ``/events/edit/epiceditor/themes/<folder>/<path>``

    **Route:** ``/events/epiceditor/themes/<folder>/<path>``

    **Methods:** ``GET``

    :param str folder: The folder that EpicEditor wants.
    :param str path: The path of the file that EpicEditor wants.
    """
    return send_from_directory(
        current_app.config['EVENTUM_STATIC_FOLDER'],
        "css/lib/epiceditor/{folder}/{path}".format(folder=folder, path=path)
    )
