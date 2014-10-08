import os

from flask import Blueprint, request, redirect, url_for, render_template, \
    send_from_directory, g, flash
from werkzeug.utils import secure_filename

from app import app
from app.lib.decorators import login_required, requires_privilege
from app.forms import UploadImageForm
from app.models import Image

media = Blueprint('media', __name__)


@media.route('/media')
@login_required
def index():
    images =Image.objects()
    form = UploadImageForm()
    return render_template('admin/media/media.html', images=images, form=form)


def allowed_file(filename):
    return '.' in filename and \
            os.path.splitext(filename)[1] in app.config['ALLOWED_UPLOAD_EXTENSIONS']

def create_filename(f, slug):
    if '.' in f.filename:
        return secure_filename(slug+os.path.splitext(f.filename)[1].lower())

@media.route('/media/upload', methods=['POST'])
@requires_privilege('edit')
def upload():
    form = UploadImageForm(request.form)
    uploaded_from = form.uploaded_from.data
    if form.validate_on_submit():
        f = request.files['image']
        if f and allowed_file(f.filename.lower()):
            filename = create_filename(f, request.form['filename'])
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = Image(filename=filename,
                          default_path=app.config['RELATIVE_UPLOAD_FOLDER']+filename,
                          creator=g.user)
            image.save()
            return redirect(url_for('.index'))
        flash("Filename %s is invalid" % f.filename)
    if form.errors:
        flash(form.errors)
    if uploaded_from:
        return redirect(uploaded_from)
    return render_template('admin/media/upload.html', form=form)

@media.route('/media/uploads/<filename>')
def file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@media.route('/media/delete/<filename>', methods=['POST'])
def delete(filename):
    if Image.objects(filename=filename).count() == 1:
        image = Image.objects().get(filename=filename)
        image.delete()
    else:
        flash('Invalid filename')
        pass
    return redirect(url_for('.index'))

@media.route('/media/view')
def view():
    return str(Image.objects())

