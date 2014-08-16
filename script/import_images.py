from app.models import Image, User
from config.flask_config import RELATIVE_UPLOAD_FOLDER, UPLOAD_FOLDER
from mongoengine import connect
from mongoengine import ValidationError

import os
import shutil


def import_from_directory(path_to_images):

    connect('eventum')
    creator = User.objects().get(gplus_id='super')

    filenames = os.listdir(path_to_images)
    filenames = [fn for fn in filenames if not fn.startswith('.')]
    failures = []

    for filename in filenames:

        if Image.objects(filename=filename).count() > 0:
            img = Image.objects().get(filename=filename)
            img.delete()

        old_path = os.path.join(path_to_images, filename)
        shutil.copy(old_path, UPLOAD_FOLDER)


        default_path = RELATIVE_UPLOAD_FOLDER + filename
        image = Image(filename=filename,
                      default_path=default_path,
                      creator=creator)
        try:
            image.save()
        except ValidationError as e:
            failures.append(filename)
            print "FAIL: %s" % filename
            print e

    print "Processed %s images." % len(filenames)
    print "%s success." %  (len(filenames) - len(failures))
    print "%s failures." % len(failures)







