from flask import Blueprint, request, redirect, url_for, render_template, \
    send_from_directory, g, flash
from app import app
from app.auth.decorators import login_required, requires_privilege
from app.media.forms import UploadImageForm
from app.media.models import Image
from werkzeug.utils import secure_filename
import os

media = Blueprint('media', __name__)


@media.route('/media')
@login_required
def index():
    images =Image.objects()
    return render_template('media/index.html', images=images)


def allowed_file(filename):
    return '.' in filename and \
            os.path.splitext(filename)[1] in app.config['ALLOWED_EXTENSIONS']

def create_filename(f, slug):
    if '.' in f.filename:
        return secure_filename(slug+os.path.splitext(f.filename)[1].lower())

@media.route('/media/upload', methods=['GET', 'POST'])
@requires_privilege('edit')
def upload_file():
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

@media.route('/media/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@media.route('/media/view')
def view():
    return str(Image.objects())