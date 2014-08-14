from app.models import BlogPost, User
from mongoengine import connect

import os
from datetime import datetime

def backfill_from_jekyll(path_to_jekyll_posts):

    connect('eventum')
    author = User.objects().get(gplus_id='super')

    filenames = os.listdir(path_to_jekyll_posts)

    for filename in filenames:
        slug = filename.split('.')[0]
        title = None
        date_published = None
        published=True
        markdown_content = ''

        with open(os.path.join(path_to_jekyll_posts, filename)) as md_file:
            content = False
            for line in md_file:
                if not title and line.startswith('## '):
                    title = line.replace('## ', '').strip()
                elif not date_published and line.startswith('### '):
                    datestring = line.replace('### ', '').strip()
                    date_published = datetime.strptime(datestring, '%d %b %Y')
                    content = True
                elif content:
                    markdown_content += line

        if BlogPost.objects(slug=slug).count() > 0:
            bp = BlogPost.objects().get(slug=slug)
            bp.delete()

        blog_post = BlogPost(title=title,
                             date_published=date_published,
                             published=published,
                             markdown_content=markdown_content,
                             slug=slug,
                             author=author)

        blog_post.save()

    print "Backfilled %s blog posts." % len(filenames)





