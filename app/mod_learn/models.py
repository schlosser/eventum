from app.mod_base.models import Post
from flask import url_for

class Resource(Post):

	def get_absolute_url(self):
		return url_for('learn', kwargs={"slug": self.slug})
