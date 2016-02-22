"""
.. module:: posts
    :synopsis: This module facilitates the generation of test blog post objects
        in the database.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

import random
from datetime import datetime, timedelta
from eventum.models import BlogPost, Image
from mongoengine.queryset import DoesNotExist
from lorem import LOREM_ADJECTIVES, LOREM_BLOG_POST

BACKUP_IMAGE_URL = 'http://lorempixel.com/800/450'


def create_posts(num_posts, superuser, printer):
    """Creates ``num_posts`` blog post objects in the database.

    :param int num_posts: The number of blog posts to create
    :param superuser: The superuser object to associate with the posts.
    :type superuser: :class:`~app.models.User`
    :param printer: The object to manage progress printing.
    :type printer: :class:`~script.cli.ProgressPrinter`

    :returns: A list of blog posts that now exist.
    :rtype: list(:class:`~app.models.BlogPost`)
    """
    print 'Generating blog posts...'
    printer.line()

    now = datetime.now()
    generator = PostGenerator(superuser, printer)
    datetimes = [now + timedelta(days=-7 * i) for i in range(num_posts)]
    successes, skips, failures = generator.create_posts(datetimes)

    printer.line()
    printer.results(len(successes), len(skips), len(failures))
    return successes + skips


class PostGenerator(object):
    """Facilitates the generation of blog posts. Intended use:

        generator = PostGenerator(superuser, printer)
        successes, skips, failures = generator.create_posts(datetimes)

    """

    def __init__(self, superuser, printer):
        """Initialize the PostGenerator.

        :param superuser: The superuser object to associate with the images.
        :type superuser: :class:`~app.models.User`
        :param printer: The object to manage progress printing.
        :type printer: :class:`~script.cli.ProgressPrinter`
        """
        self.superuser = superuser
        self.printer = printer
        self.index = 0
        self.successes = []
        self.failures = []
        self.skips = []
        self.images = None

    def create_posts(self, datetimes):
        """Creates several blog posts, one for each of the ``datetimes`` passed
        as an argument.

        :param datetimes: The published dates of each of the posts to make.
        :type datetimes: list(:class:`datetime.datetime`)

        :returns: 3-tuple of (successes, skips, failures)
        :rtype: tuple(list(:class:`~app.models.BlogPost`))
        """
        for dt in datetimes:
            self.date_published = dt
            self.next()
        return self.successes, self.skips, self.failures

    def next(self):
        """Create the next :class:`~app.models.BlogPost` object if it doesn't
        already exist and then add it to ``self.successes`` or ``self.skips``
        appropriately.
        """
        self.index += 1
        slug = self._slug()
        self.printer.begin_status_line('<BlogPost slug="{}">'.format(slug))
        try:
            blog_post = BlogPost.objects.get(slug=slug)
            self.skips.append(blog_post)
            self.printer.status_skip()
        except DoesNotExist:
            blog_post = self.make_post()
            blog_post.save()
            self.successes.append(blog_post)
            self.printer.status_success()

    def make_post(self):
        """Create and return a new :class:`~app.models.BlogPost` object using
        the configuration variables on the ``self``.

        :returns: The blog post.
        :rtype: :class:`~app.models.BlogPost`
        """
        return BlogPost(title=self._title(),
                        author=self.superuser,
                        markdown_content=self._markdown_content(),
                        images=self._images(),
                        featured_image=self._featured_image(),
                        slug=self._slug(),
                        categories=self._categories(),
                        tags=self._tags(),
                        published=True,
                        date_published=self.date_published,
                        posted_by=self.superuser)

    def _title(self):
        """Get the next post title.

        :returns: The title.
        :rtype: str
        """
        return '{} Test Post {}'.format(random.choice(LOREM_ADJECTIVES),
                                        self.index)

    def _slug(self):
        """Get the next post slug.

        :returns: The slug.
        :rtype: str
        """
        return 'test-post-{}'.format(self.index)

    def _categories(self):
        """Test posts don't have categories.

        :returns: ``[]``.
        :rtype: list
        """
        return []

    def _tags(self):
        """Test posts don't have tags.

        :returns: ``[]``.
        :rtype: list
        """
        return []

    def _featured_image(self):
        """Select a random featured image.

        :returns: The image
        :rtype: :class:`~app.models.Image`
        """
        return random.choice(self._images())

    def _images(self):
        """Gets a list of images from the database if any exist.

        :returns: The images.
        :rtype: list(:class:`~app.models.Image`)
        """
        # Fetch self.images if it hasn't been fetched
        if self.images is None:
            self.images = list(Image.objects().limit(5))
        return self.images

    def _markdown_content(self):
        """Get the markdown content for the blog post.  Images are inserted
        into the markdown, but they are external links, not linked to images
        in the database.
        """

        # TODO: fix using mongo images in blog posts. Currently, we need app
        # context in order to attach an image onto a blog post, because
        # Post.clean() calls Image.url() for every Image with it's filename in
        # the markdown content, which calls url_for() which requires context.
        #
        # Breaks things:
        # filenames = [image.filename for image in self._images()[:2]]

        # The blog post LOREM has two format string spots for images.
        filenames = [BACKUP_IMAGE_URL for i in range(2)]

        return LOREM_BLOG_POST.format(*filenames)
