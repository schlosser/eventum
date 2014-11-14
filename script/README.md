# `/script`

Helper scripts.

## Notable files

- `backfill_blog.py`: A script to backfill the `eventum` mongo database from the old blog posts. To get the old website data, run `git submodule update --init`.  To run, run `python manage.py --backfill-blog`.
- `backfill_blog.py`: A script to backfill the `eventum` mongo database from the old images. To get the old website data, run `git submodule update --init`.  To run, run `python manage.py --import-images`.
