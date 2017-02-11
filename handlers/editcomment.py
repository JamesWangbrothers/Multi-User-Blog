from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from helpers import *

class EditComment(BaseHandler):
	"""Handler for edit a comment"""
	# @comment_exists
	# @user_logged_in
	def get(self, post_id, post_user_id, comment_id):
		if self.user and self.user.key().id() == int(post_user_id):
			postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
			key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
			comment = db.get(key)

			self.render('editcomment.html', content=comment.content)

		elif not self.user:
			self.redirect('/login')

		else:
			self.write("You don't have permission to edit this comment")

	# @comment_exists
	# @user_logged_in
	def post(self, post_id, post_user_id, comment_id):
		if not self.user:
			return

		if self.user and self.user.key().id() == int(post_user_id):
			content = self.request.get('content')

			postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
			key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
			comment = db.get(key)

			comment.content = content
			comment.put()

			self.redirect('/' + post_id)

		else:
			self.write("You don't have permission to edit this comment.")