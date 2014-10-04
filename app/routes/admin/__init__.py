from admin import admin
from auth import auth
from events import events
from resources import resources
from media import media
from posts import posts
from users import users
from whitelist import whitelist

# note: silences pyflakes unused variables
assert (admin,
        auth,
        events,
        resources,
        media,
        posts,
        users,
        whitelist)
