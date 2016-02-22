"""
.. module:: images
    :synopsis: This module facilitates the generation of test image objects in
        the database.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import urllib
from os.path import exists
from eventum.models import Image
from eventum.config import eventum_config

BASE_URL = "http://lorempixel.com/{}/{}/"
BASE_FILENAME = "test_photo_{}x{}.jpeg"


def create_images(num_images, superuser, printer):
    """Creates ``num_images`` image objects in the database.  It will download
    sample images from http://lorempixel.com, and add database entries.

    :param int num_images: The number of images to create
    :param superuser: The superuser object to associate with the images.
    :type superuser: :class:`~app.models.User`
    :param printer: The object to manage progress printing.
    :type printer: :class:`~script.cli.ProgressPrinter`

    :returns: A list of images that now exist.
    :rtype: list(:class:`~app.models.Image`)
    """
    print "Generating images..."
    printer.line()

    successes = []
    failures = []
    skips = []
    for width in range(400, 1600, (1600 - 400) / num_images):
        height = width / 2
        filename = BASE_FILENAME.format(width, height)
        path = eventum_config.EVENTUM_UPLOAD_FOLDER + filename
        url = BASE_URL.format(width, height)

        printer.begin_status_line(filename)

        # Download image if it doesn't exist already
        if not exists(path):
            try:
                urllib.urlretrieve(url, path)
            except IOError:
                failures.append((filename, ''))
                printer.status_fail()
                continue  # Failed to download, move on to the next image.

        # Insert or fetch image from database
        if Image.objects(filename=filename).count() == 0:
            image = Image(filename=filename,
                          default_path=path,
                          creator=superuser)
            image.save()
            successes.append((filename, path))
            printer.status_success()
        else:
            skips.append((filename, path))
            printer.status_skip()

    printer.line()
    printer.results(len(successes), len(skips), len(failures))
    return successes + skips
