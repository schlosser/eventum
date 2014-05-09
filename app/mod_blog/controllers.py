from app import app
from flask import Blueprint, render_template, request, send_from_directory, \
    abort, redirect, url_for, g, flash
from app.mod_blog.models import BlogPost
from app.mod_media.models import Image
from app.mod_blog.forms import CreateBlogPostForm
from app.mod_auth.decorators import login_required, requires_privilege
from bson.objectid import ObjectId

mod_blog = Blueprint('blog', __name__)

@mod_blog.route('/blog')
def blog():
	return render_template('blog/index.html', posts=BlogPost.objects())

@mod_blog.route('/blog/posts')
@login_required
def posts():
    return render_template('blog/posts.html', posts=BlogPost.objects())

@mod_blog.route('/blog/post/<slug>')
def post(slug):
    if BlogPost.objects(slug=slug).count() != 1:
        abort(404)
    post = BlogPost.objects().get(slug=slug)

    if not post.published:
        abort(404)
    return render_template('blog/post.html', post=post)

@mod_blog.route('/blog/posts/new', methods=['GET', 'POST'])
@requires_privilege('edit')
def new_post():
    form = CreateBlogPostForm(request.form)
    if form.validate_on_submit():
        print request.form
        print form.images.data
        post = BlogPost(title=form.title.data,
                        slug=form.slug.data,
                        images=[Image.objects().get(filename=fn) for fn in form.images.data],
                        markdown_content=form.body.data,
                        author=g.user)
        post.save()
        return redirect(url_for('.posts'))
    images = Image.objects()
    return render_template('blog/edit_post.html', form=form, images=images)

@mod_blog.route('/blog/posts/edit/<post_id>', methods=['GET', 'POST'])
@requires_privilege('edit')
def edit_post(post_id):
    object_id = ObjectId(post_id)
    if BlogPost.objects(id=object_id).count() != 1:
        abort(501)

    post = BlogPost.objects().with_id(object_id)
    if request.method == 'POST':
        form = CreateBlogPostForm(request.form)
        if form.validate_on_submit():
            post.title=form.title.data
            post.slug=form.slug.data
            post.markdown_content = form.body.data
            post.images = [Image.objects().get(filename=fn) for fn in form.images.data]
            post.save()
            return redirect(url_for('.posts'))
    form = CreateBlogPostForm(request.form,
                              title=post.title,
                              slug=post.slug,
                              body=post.markdown_content,
                              images=[image.filename for image in post.images])
    images = [image for image in Image.objects() if image not in post.images]
    return render_template('blog/edit_post.html', form=form, post=post, images=images)

@mod_blog.route('/blog/posts/delete/<post_id>', methods=['POST'])
def delete(post_id):
    object_id = ObjectId(post_id)
    if BlogPost.objects(id=object_id).count() == 1:
        post = BlogPost.objects().with_id(object_id)
        post.delete()
    else:
        flash('Invalid event id')
        # print "Invalid event id"
        pass
    return redirect(url_for('.posts'))


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
    return redirect(url_for('.posts'))


@mod_blog.route('/blog/posts/publish/<post_id>', methods=['POST'])
@requires_privilege('publish')
def publish_event(post_id):
    return set_published_status(post_id, True)


@mod_blog.route('/blog/posts/unpublish/<post_id>', methods=['POST'])
@requires_privilege('publish')
def unpublish_event(post_id):
    return set_published_status(post_id, False)

@mod_blog.route('/blog/posts/edit/epiceditor/themes/<folder>/<path>')
@mod_blog.route('/blog/posts/epiceditor/themes/<folder>/<path>')
@login_required
def fetch_epiceditor_themes(folder, path):
    return send_from_directory(app.static_folder, "css/epiceditor/%s/%s" % (folder, path))
