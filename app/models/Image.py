"""
.. module:: Image
    :synopsis: A image database model.

.. moduleauthor:: Dan Schlosser <dan@danrs.ch>
"""

from flask import url_for
from mongoengine import ValidationError, signals
from app import db
from config.flask_config import ALLOWED_UPLOAD_EXTENSIONS, BASEDIR, \
                                RELATIVE_DELETE_FOLDER
from datetime import datetime
import PIL, re, os
now = datetime.now


class Image(db.Document):
    """
    :ivar date_created: :class:`mongoengine.DateTimeField` - The date when the
        document was created, localized to the server.
    :ivar date_modified: :class:`mongoengine.DateTimeField` - The date when the
        document was last modified, localized to the server.
    :ivar filename: :class:`mongoengine.StringField` - The filename with
        extension of the image.
    :ivar creator: :class:`mongoengine.ReferenceField` - Reference to the User
        that uploaded the photo.
    :ivar caption: :class:`mongoengine.StringField` - A caption for the photo.
    :ivar source: :class:`mongoengine.StringField` - A source credit for the
        picture, if one is needed.
    :ivar default_path: :class:`mongoengine.StringField` - The path the the
        version of the image that should be used by default.
    :ivar versions: :class:`mongoengine.DictField` - A dictionary of sizes to
        file paths.
    """

    # MongoEngine ORM metadata
    meta = {
        'allow_inheritance': True,
        'indexes': ['creator'],
        'ordering': ['-date_created']
    }

    date_created = db.DateTimeField(default=now, required=True)
    date_modified = db.DateTimeField(default=now, required=True)
    filename = db.StringField(unique=True,
                              max_length=255,
                              required=True,
                              regex="([a-z]|[A-Z]|[0-9]|\||-|_|@|\(|\))*(" + \
                                    ('|'.join(ALLOWED_UPLOAD_EXTENSIONS)+')'))
    creator = db.ReferenceField('User', required=True)
    caption = db.StringField()
    source = db.StringField()
    default_path = db.StringField(required=True)
    versions = db.DictField(required=True)

    def url(self):
        """Returns the URL path that points to the image.

        :returns: The URL path like ``"/static/img/cat.jpg"``.
        :rtype: str
        """
        return url_for('media.file', filename=self.filename)

    def clean(self):
        """Called by Mongoengine on every ``.save()`` to the object.

        Update date_modified and populate the versions dict.

        :raises: :class:`ValidationError`
        """
        VALID_PATHS = re.compile("^(" + BASEDIR + "|http://|https://).*$")
        self.date_modified = now()
        if not VALID_PATHS.match(self.default_path):
            self.default_path = os.path.join(BASEDIR, self.default_path)
        if self.default_path and self.default_path not in self.versions.values():
            try:
                width, height = PIL.Image.open(self.default_path).size
                self.versions['%sx%s' % (width, height)] = self.default_path
            except IOError:
                raise ValidationError('File %s does not exist.' % self.default_path)

    def pre_validate(form):
        """Called by Mongoengine before the validation occurs.

        Ensure that the versions dictionary contains keys of the form
        ``"<width>x<height>"``, where ``width`` and ``height`` are the size of
        the image at the path.

        :raises: :class:`ValidationError`
        """
        for size,path in form.versions:
            try:
                width, height = PIL.Image.open(path).size
                if size != '%sx%s' % (width, height):
                    error = 'Key %s improperly describes image %s', (size, path)
                    raise ValidationError(error)
            except IOError:
                error = 'File %s does not exist.' % form.default_path
                raise ValidationError(error)

    @classmethod
    def post_delete(klass, sender, document, **kwargs):
        """Called by Mongoengine after the object has been delted.

        Moves the deleted image's assocaited files to the DELETED_FOLDER.
        """
        for size, old_path in document.versions.iteritems():
            _, filename = os.path.split(old_path)
            delete_folder = RELATIVE_DELETE_FOLDER
            if not os.path.isdir(delete_folder):
                os.mkdir(delete_folder)
            new_path = os.path.join(delete_folder, filename)
            try:
                os.rename(old_path, new_path)
            except IOError:
                pass

    def __unicode__(self):
        """This image, as a unicode string.

        :returns: The filename of the image.
        :rtype: str
        """
        return self.filename

    def __repr__(self):
        """The representation of this image.

        :returns: The image's details.
        :rtype: str
        """
        rep = 'Photo(filename=%r, default_path=%r, caption=%r)' % \
        (self.filename, self.default_path, self.caption)
        return rep

# Connects the ``post_delte`` method using the signals library.
signals.post_delete.connect(Image.post_delete, sender=Image)
