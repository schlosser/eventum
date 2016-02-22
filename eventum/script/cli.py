"""
.. module:: cli
    :synopsis: This module contains classes and methods for creating better
        command line interfaces.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>

Currently, this module is only used within the `script` folder.  If we want to
add fancy command line interfaces for the Flask app, we should move this into
/app/lib.
"""


class CLIColor(object):
    """An object that holds methods for printing styled text to the console. All
    methods on this class are static, so you should simply call::

        print CLIColor.ok_blue('Test Message')

    Methods may also be chained in order to add multiple effects::

        print CLIColor.underline(CLIColor.fail('Fatal Error'))

    """

    ENDC = '\033[0m'

    @staticmethod
    def header(message):
        """Returns ``message``, formatted to be printed in header.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[95m' + message + CLIColor.ENDC

    @staticmethod
    def ok_blue(message):
        """Returns ``message``, formatted to be printed in ok_blue.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[94m' + message + CLIColor.ENDC

    @staticmethod
    def ok_green(message):
        """Returns ``message``, formatted to be printed in ok_green.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[92m' + message + CLIColor.ENDC

    @staticmethod
    def warning(message):
        """Returns ``message``, formatted to be printed in warning.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[93m' + message + CLIColor.ENDC

    @staticmethod
    def fail(message):
        """Returns ``message``, formatted to be printed in fail.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[91m' + message + CLIColor.ENDC

    @staticmethod
    def bold(message):
        """Returns ``message``, formatted to be printed in bold.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[1m' + message + CLIColor.ENDC

    @staticmethod
    def underline(message):
        """Returns ``message``, formatted to be printed in underline.

        :param str message: The text to style.

        :returns: The styled text, ready to be printed.
        :rtype: str
        """
        return '\033[4m' + message + CLIColor.ENDC


class ProgressPrinter(object):
    """A class that facilitates printing status tables like::

        ----------------------------------------
        test_photo_1.jpeg                Success
        test_photo_2.jpeg                Success
        test_photo_3.jpeg                Success
        test_photo_4.jpeg                Success
        test_photo_5.jpeg                Success
        test_photo_6.jpeg                Success
        test_photo_7.jpeg                Success
        test_photo_8.jpeg                Success
        test_photo_9.jpeg                Success
        test_photo_10.jpeg               Success
        test_photo_11.jpeg               Success
        test_photo_12.jpeg               Success
        ----------------------------------------
        Done: 12 successful, 0 skipped, 0 failed

    The above table might be generated as follows:

        printer = ProgressPrinter()
        successes = []
        printer.line()
        for i in range(1, 13):
            printer.begin_status_line('test_photo_{}.jpeg'.format(i))
            # Do work
            successes.append(i)
            printer.status_success()
        printer.line()
        printer.results(successes, [], [])

    """

    # Each of these status messages has to be the same width, so that they can
    # be right-aligned in the table.
    STATUS_SUCCESS = 'Success'
    STATUS_FAIL = '   Fail'
    STATUS_SKIP = '   Skip'
    # Amount of room to leave for status message, plus a 1-character space.
    SPACE = len(STATUS_SUCCESS) + 1

    def __init__(self, quiet=False, width=40):
        """Sets up new ProgressPrinter.

        :param bool quiet: If True, this printer will never print anything.
        :param int width: Width in characters of the table to print.
        """
        self.quiet = quiet
        self.width = width

    def results(self, successes, skips, failures):
        """Print out the number of successes, skips, and failures that exist.
        Output will be colored appropriately.

        example::

            printer.results(12, 0, 0)
            # Done: 12 successful, 0 skipped, 0 failed

        :param in successes: Number of successful operations.
        :param in skips: Number of skipped operations.
        :param in failures: Number of failed operations.
        """
        if self.quiet:
            return

        print "Done:",

        if successes:
            print CLIColor.ok_green("{} successful,".format(successes)),
        else:
            print "0 successful,",

        print "{} skipped,".format(skips),

        if failures:
            print CLIColor.ok_green("{} failed".format(failures)),
        else:
            print "0 failed"

    def line(self):
        """Prints out a line of ``-`` characters to stdout."""
        if not self.quiet:
            print "-" * self.width

    def begin_status_line(self, item):
        """Print the first half of a status line to the console. After calling
        this function, it is expected that a call to :func:`status_success`,
        :func:`status_skip`, or :func:`status_failure` will follow.

        :param str item: The text to print on the left half of the status line.
        """
        if not self.quiet:
            print item + (" " * (self.width - self.SPACE - len(item))),

    def status_success(self):
        """Print out "Success" to the end of a status line.  It is expected
        that this function is only called after a call to
        :func:`begin_status_line`.
        """
        if not self.quiet:
            print self.STATUS_SUCCESS

    def status_skip(self):
        """Print out "Skip" to the end of a status line.  It is expected that
        this function is only called after a call to :func:`begin_status_line`.
        """
        if not self.quiet:
            print self.STATUS_SKIP

    def status_fail(self):
        """Print out "Fail" to the end of a status line.  It is expected that
        this function is only called after a call to :func:`begin_status_line`.
        """
        if not self.quiet:
            print self.STATUS_FAIL
