from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from helpers import *
from decorators import *

class DeleteComment(BaseHandler):
	"""Handler for delete a comment"""

	@comment_exists
	@user_logged_in
	@user_owns_comment
	def get(self, post_id, post_user_id, comment_id):
		postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
		comment_key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
		comment = db.get(comment_key)
		comment.delete()

		self.redirect('/' + post_id)
