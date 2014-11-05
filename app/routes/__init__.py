from __future__ import absolute_import

from app.routes.blog import blog
from app.routes.client import client
from app.routes.base import base

# note: silences pyflakes unused variables
assert (absolute_import,
        base,
        blog,
        client)
