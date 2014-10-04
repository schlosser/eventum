from __future__ import absolute_import

from app.routes.blog import blog
from app.routes.client import client

# note: silences pyflakes unused variables
assert (absolute_import,
        blog,
        client)
