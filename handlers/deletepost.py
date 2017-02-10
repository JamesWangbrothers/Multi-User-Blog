from google.appengine.ext import db
from handlers.blog import BaseHandler
from helpers import *

class DeletePost(BaseHandler):
	"""Handler for delete a post"""
	def get(self, post_id, post_user_id):

		if self.user and post.user.key().id() == int(post_user_id):
			key = db.Key.from_path('Post', int(post_id), parent=blog_key())
			post = db.get(key)
			post.delete()
			self.redirect("/")
		elif not self.user:
			self.redirect("/")
		else:
			key = db.Key.from_path('Post', int(post_id), parent=blog_key())
			post = db.get(key)

			comments = db.GqlQuery(
				"select * from Comment where ancestor is :1 order by created desc limit 10", key)

			error = "You don't have permission to delete this post"
			self.render("permalink.html", post=post, comments=comments, error=error)
