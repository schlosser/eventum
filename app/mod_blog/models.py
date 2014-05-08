from app.mod_base.models import Post
from app.mod_blog.utils import truncate_html
from flask import url_for

class BlogPost(Post):

	def snippet(self, length=100, truncate_text="..."):
		return truncate_html(self.html_content, length, truncate_text)

	def get_absolute_url(self):
		return url_for('blog.post', slug=self.slug)




