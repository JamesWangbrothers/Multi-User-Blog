from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from helpers import *
from decorators import *

class DeletePost(BaseHandler):
	"""Handler for delete a post"""

	@post_exists
	@user_owns_post
	@user_logged_in
	def get(self, post_id, post_user_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		post.delete()

		self.redirect("/")


