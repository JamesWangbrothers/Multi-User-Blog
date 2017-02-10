from google.appengine.ext import db
from handlers.blog import BaseHandler
from helpers import *

class DeleteComment(BaseHandler):
	"""Handler for delete a comment"""
	def get(self, post_id, post_user_id, comment_id):
		if self.user and self.user.key().id() == int(post_user_id):
			postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
			key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
			comment = Comment.get(key)
			comment.delete()

			self.redirect('/' + post_id)

		elif not self.user:
			self.redirect('/login')
		else:
			self.write("You don't permission to delete this comment")