from __future__ import absolute_import

from app.routes.blog import blog
from app.routes.home import home

assert (absolute_import,
        blog,
        home)