import os
import unittest
from fnmatch import fnmatch

from sys import path
path.append('../')


class TestDocumentation(unittest.TestCase):

    APP_ROOT = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    EXCLUDES = set(open('../.gitignore').read().split('\n') + ['.git'])
    README = 'README.md'

    def test_readmes(self):
        """All directories not in the gitignore should have `README.md` files
        in them.
        """

        for root, dirs, filenames in os.walk(self.APP_ROOT):
            # Ignore all subdirectories of directories that match the EXCLUDES
            dirs[:] = [d for d in dirs if not
                       any(fnmatch(d, pattern) for pattern in self.EXCLUDES)]

            for d in dirs:
                readme = os.path.join(root, d, self.README)
                relpath = os.path.relpath(os.path.join(root, d), self.APP_ROOT)
                self.assertTrue(
                    os.path.isfile(readme),
                    msg=self.README + " must be created in " + relpath)

if __name__ == '__main__':
    unittest.main()
