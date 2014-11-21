from admin import admin
from auth import auth
from events import events
from media import media
from posts import posts
from users import users
from whitelist import whitelist

# note: silences pyflakes unused variables
assert (admin and
        auth and
        events and
        media and
        posts and
        users and
        whitelist)
