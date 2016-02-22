## Refactor Progress

- new package structure
- remove `Pillow` dependency
- remove `versions` field from the `Image` model, because we never wrote any code to resize images. 


## TODO

### p1

- Fix the global `e` object
- Make SCSS not suck
    + deprecation warnings
    + imports shouldn't be duplicative (one big blog of css should suffice)
- Fix `migration.py` and DB population
- Uploaded images should be stored outside of the package (in the client area)
    + This will require new mandatory config variables.
- oooph change the default profile picture and event image...

### p3

- Automatic image resizing on upload (in the background)
- better error logging
    + `Image.py:post_delete`
- `Image.default_path` should be `Image.path` now.
- Allow users to change profile pictures
- Styles for tag interface
- Allow images to be set as featured immediately upon adding them (without needing to go back later).
- User editing page delete button is borked.
