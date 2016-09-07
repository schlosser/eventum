"""
.. module:: media
    :synopsis: All routes on the ``media`` Blueprint.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import os

from flask import Blueprint, request, redirect, url_for, render_template, \
    send_from_directory, g, flash, jsonify, current_app
from werkzeug.utils import secure_filename

from eventum.lib.decorators import login_required, requires_privilege
from eventum.forms import UploadImageForm
from eventum.models import Image
from eventum.routes.base import ERROR_FLASH

media = Blueprint('media', __name__)


@media.route('/media', methods=['GET'])
@login_required
def index():
    """View all of the uploaded images.

    **Route:** ``/admin/media``

    **Methods:** ``GET``
    """
    images = Image.objects()
    form = UploadImageForm()
    return render_template('eventum_media/media.html',
                           images=images,
                           form=form)


def allowed_file(filename):
    """Returns True if ``filename`` is a valid filename.  It must have an
    extension and its extension is in the allowed uploaded extensions.

    :returns: True if ``filename`` is valid.
    :rtype: bool
    """
    return (
        '.' in filename and os.path.splitext(filename)[1] in
        current_app.config['EVENTUM_ALLOWED_UPLOAD_EXTENSIONS']
    )


def create_filename(f, slug):
    """Creates the filename to save.

    :param file f: The file make the filename from
    :param str slug: The file's name.

    :returns: The secure filename, to save to disk.
    :rtype: str
    """
    if '.' in f.filename:
        return secure_filename(slug + os.path.splitext(f.filename)[1].lower())


@media.route('/media/upload', methods=['POST'])
@requires_privilege('edit')
def upload():
    """Upload an image to Eventum

    :returns: A JSON containing the status of the file upload, or error
              messages, if any.
    :rtype: json
    """
    form = UploadImageForm(request.form)
    if form.validate_on_submit():
        f = request.files['image']
        if f:
            filename = create_filename(f, request.form['filename'])
            upload_folder = current_app.config['EVENTUM_UPLOAD_FOLDER']
            if not os.path.isdir(upload_folder):
                os.mkdir(upload_folder)
            f.save(os.path.join(upload_folder, filename))
            default_path = os.path.join(
                current_app.config['EVENTUM_UPLOAD_FOLDER'],
                filename,
            )
            image = Image(filename=filename,
                          default_path=default_path,
                          creator=g.user)
            image.save()
            return jsonify({"status": "true"})
    if form.errors:
        return jsonify(form.errors)
    return jsonify({"status": "error"})


@media.route('/media/uploads/<filename>', methods=['GET'])
def file(filename):
    """View the raw image file for the file with name ``filename``.

    **Route:** ``/admin/media/uploads/<filename>``

    **Methods:** ``GET``

    :param str filename: The filename of the image to show.
    """
    return send_from_directory(current_app.config['EVENTUM_UPLOAD_FOLDER'],
                               filename)


@media.route('/media/delete/<filename>', methods=['POST'])
@requires_privilege('edit')
def delete(filename):
    """View all of the uploaded images.

    **Route:** ``/admin/media/delete/<filename>``

    **Methods:** ``POST``
    """
    if Image.objects(filename=filename).count() == 1:
        image = Image.objects().get(filename=filename)
        image.delete()
    else:
        flash('Invalid filename', ERROR_FLASH)
    return redirect(url_for('.index'))


@media.route('/media/image-view', methods=['GET'])
def select():
    """Displays all uploaded images, with mode depending on parameter passed in

    **Route:** ``/admin/media/image``

    **Methods:** ``GET``
    """
    images = Image.objects()

    fmt = "eventum_media/image_{image_mode!s}.html"
    template_name = fmt.format(image_mode=request.args.get("mode"))
    return render_template(template_name, images=images)
