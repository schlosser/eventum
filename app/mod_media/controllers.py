from flask import Blueprint, request, redirect, url_for, render_template, \
    send_from_directory, g, flash
from app import app
from app.mod_auth.decorators import login_required, requires_privilege
from app.mod_media.forms import UploadImageForm
from app.mod_media.models import Image
from werkzeug.utils import secure_filename
import os

mod_media = Blueprint('media', __name__)


@mod_media.route('/media')
@login_required
def media():
    images = [{
        "url": url_for('.uploaded_file', filename=photo.filename),
        "filename":photo.filename
        } for photo in Image.objects()]
    print images
    return render_template('media/index.html', images=images)


def allowed_file(filename):
    print os.path.splitext(filename)[1]
    print app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
            os.path.splitext(filename)[1] in app.config['ALLOWED_EXTENSIONS']

def create_filename(f, slug):
    if '.' in f.filename:
        return secure_filename(slug+os.path.splitext(f.filename)[1].lower())

@mod_media.route('/media/upload', methods=['GET', 'POST'])
@requires_privilege('edit')
def upload_file():
    print request.form
    form = UploadImageForm(request.form)
    if form.validate_on_submit():
        f = request.files['image']
        if f and allowed_file(f.filename.lower()):
            filename = create_filename(f, request.form['filename'])
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = Image(filename=filename,
                          default_path='app/static/img/'+filename,
                          creator=g.user)
            image.save()
            return redirect(url_for('.media'))
        flash("Filename %s is invalid" % f.filename)
    if form.errors:
        flash(form.errors)
    return render_template('media/upload.html', form=form)

@mod_media.route('/media/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@mod_media.route('/media/view')
def view():
    return str(Image.objects())