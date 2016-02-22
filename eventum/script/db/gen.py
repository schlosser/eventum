"""
.. module:: gen
    :synopsis: This module runs scripts that load the database with test
        configurations. To run the scripts, run ``python manage.py db`` from
        the root directory.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""

from mongoengine import connect
from mongoengine.queryset import DoesNotExist
from sys import argv, exit
from eventum.models import User, Event, EventSeries, Image, BlogPost
from eventum.script.cli import CLIColor, ProgressPrinter
from eventum.config import eventum_config
from images import create_images
from events import create_events
from posts import create_posts

argv0 = argv[0]

ACTION_IMAGES = 'images'
ACTION_EVENTS = 'events'
ACTION_POSTS = 'posts'
ACTION_ALL = 'all'
ACTIONS = [ACTION_IMAGES, ACTION_EVENTS, ACTION_POSTS, ACTION_ALL]

FLAGS = [
    (['-w', '--wipe'], 'Wipes related databases.  If omitted, records that '
                       'already exist will not be updated.'),
    (['-f', '--force'], 'Doesn\'t ask before wiping database.  Only relevant '
                        'if the --wipe option is used.'),
    (['-q', '--quiet'], 'Runs with minimal output')
]


class TestDataGenerator(object):
    """Loads the database with test data."""

    def __init__(self, command, quiet, wipe, force):
        """Initializes the TestDataGenerator

        :param str command: One of the four following commands::

            ACTION_IMAGES: Create new :class:`~app.models.Image` objects.
            ACTION_EVENTS: Create new :class:`~app.models.Event` and
                            :class:`~app.models.EventSeries` objects.
             ACTION_POSTS: Create new :class:`~app.models.BlogPost` objects.
               ACTION_ALL: Do all of the above.

        :param flags: Flags passed to the function.  We assume all are valid.
        :type flags: set(str)
        """
        self.should_gen_images = command in (ACTION_IMAGES, ACTION_ALL)
        self.should_gen_events = command in (ACTION_EVENTS, ACTION_ALL)
        self.should_gen_posts = command in (ACTION_POSTS, ACTION_ALL)
        self.quiet = quiet
        self.wipe = wipe
        self.force = force

    def warn(self, db_name):
        """Print out a warning that we are about to wipe ``db_name``.  Prompts
        the user to confirm this deletion.

        If the ``--force`` flag is used, this check is skipped.

        :param str db_name: The name of the database to delete.
        """
        if not self.force:
            print CLIColor.underline(
                CLIColor.fail('WARNING!!! You are about wipe the '
                              '{} database!'.format(db_name)))
            cont = ''
            while cont == '':
                cont = raw_input('Do you want to continue? (yes/no): ')
            if cont[0] not in ('y', 'Y'):  # if the answer doesn't start with y
                print ('Exiting...')
                exit(1)

    def run(self):
        """Run the generation.  Uses the configurations passed to
        func:`__init__`.
        """

        # Setup: db connection, superuser, and printer.
        connect(eventum_config.MONGODB_SETTINGS['DB'])
        try:
            superuser = User.objects().get(gplus_id='super')
        except DoesNotExist:
            print ('Failed to get superuser.  Try running:\n'
                   '\texport GOOGLE_AUTH_ENABLED=TRUE')
        printer = ProgressPrinter(self.quiet)

        # Images
        if self.should_gen_images:
            if self.wipe:
                self.warn('Image')
                print CLIColor.warning('Wiping Image database.')
                Image.drop_collection()
            create_images(12, superuser, printer)

        # Blog posts
        if self.should_gen_posts:
            if self.wipe:
                self.warn('BlogPost')
                print CLIColor.warning('Wiping BlogPost database.')
                BlogPost.drop_collection()
            create_posts(10, superuser, printer)

        # Events and event series
        if self.should_gen_events:
            if self.wipe:
                self.warn('Event and EventSeries')
                print CLIColor.warning('Wiping Event database.')
                Event.drop_collection()
                print CLIColor.warning('Wiping EventSeries database.')
                EventSeries.drop_collection()
            create_events(superuser, printer)
