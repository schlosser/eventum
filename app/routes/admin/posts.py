from flask import Blueprint, render_template, request, send_from_directory, \
    abort, redirect, url_for, g, flash

from bson.objectid import ObjectId
from bson.objectid import InvalidId

from mongoengine.errors import DoesNotExist, ValidationError

from app import app
from app.models import BlogPost, Image
from app.forms import CreateBlogPostForm, UploadImageForm
from app.lib.decorators import login_required, requires_privilege

posts = Blueprint('posts', __name__)

@posts.route('/posts')
@login_required
def index():
    all_posts = BlogPost.objects().order_by('published', '-date_published')
    return render_template('admin/posts/posts.html', posts=all_posts)

@posts.route('/posts/new', methods=['GET', 'POST'])
@requires_privilege('edit')
def new():
    form = CreateBlogPostForm(request.form)
    upload_form = UploadImageForm()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data,
                        slug=form.slug.data,
                        published=form.published.data,
                        images=[Image.objects().get(filename=fn) for fn in form.images.data],
                        markdown_content=form.body.data,
                        author=g.user)
        post.save()
        return redirect(url_for('.index'))
    images = Image.objects()
    return render_template('admin/posts/edit.html', user=g.user, form=form,
                           images=images, upload_form=upload_form)

@posts.route('/posts/edit/<post_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit(post_id):
    try:
        object_id = ObjectId(post_id)
    except InvalidId:
        return abort(404)
    try:
        post = BlogPost.objects().with_id(object_id)
    except (DoesNotExist, ValidationError):
        flash('Cannot find blog post with id %s.' % post_id)
        return redirect(url_for('.index'))

    if request.method == 'POST':
        form = CreateBlogPostForm(request.form)
        if form.validate_on_submit():
            was_published = post.published
            should_be_published = form.published.data
            post.title=form.title.data
            post.slug=form.slug.data
            post.markdown_content = form.body.data
            post.images = [Image.objects().get(filename=fn) for fn in form.images.data]
            if form.featured_image.data:
                post.featured_image = Image.objects().get(filename=form.featured_image.data)
            else:
                post.featured_image = None
            post.save()
            if was_published != should_be_published:
                if was_published:
                    set_published_status(post.id, False)
                else:
                    set_published_status(post.id, True)
            return redirect(url_for('.index'))
    upload_form = UploadImageForm()
    featured_image = post.featured_image.filename if post.featured_image else None
    form = CreateBlogPostForm(request.form,
                              title=post.title,
                              slug=post.slug,
                              published=post.published,
                              body=post.markdown_content,
                              images=[image.filename for image in post.images],
                              featured_image=featured_image)
    images = [image for image in Image.objects() if image not in post.images]
    return render_template('admin/posts/edit.html', user=g.user, form=form,
                           post=post, images=images, upload_form=upload_form)

@posts.route('/posts/delete/<post_id>', methods=['POST'])
def delete(post_id):
    object_id = ObjectId(post_id)
    if BlogPost.objects(id=object_id).count() == 1:
        post = BlogPost.objects().with_id(object_id)
        post.delete()
    else:
        flash('Invalid event id')
        # print "Invalid event id"
        pass
    return redirect(url_for('.index'))


def set_published_status(post_id, status):
    object_id = ObjectId(post_id)
    if BlogPost.objects(id=object_id).count() == 1:
        post = BlogPost.objects().with_id(object_id)
        if status != post.published:
            post.published = status
            # TODO Actually publish/unpublish the post here
            if post.published:
                flash('Blogpost published')
            else:
                flash('Blogpost unpublished')
            post.save()
        else:
            flash("The blog post had not been published.  No changes made.")
    else:
        flash('Invalid post id')
        # print "Invalid post id"
        pass
    return redirect(url_for('.index'))

@posts.route('/posts/edit/epiceditor/themes/<folder>/<path>')
@posts.route('/posts/epiceditor/themes/<folder>/<path>')
@posts.route('/events/edit/epiceditor/themes/<folder>/<path>')
@posts.route('/events/epiceditor/themes/<folder>/<path>')
@login_required
def fetch_epiceditor_themes(folder, path):
    return send_from_directory(app.static_folder, "css/lib/epiceditor/%s/%s" % (folder, path))

@posts.route('/posts/dad')
def dad():
    for post in BlogPost.objects():
        post.delete()
    return "son"

@posts.route('/posts/view')
def view_all_posts():
    return str(BlogPost.objects())

