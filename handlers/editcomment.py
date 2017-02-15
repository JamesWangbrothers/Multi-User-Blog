from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from helpers import *
from decorators import *

class EditComment(BaseHandler):
	"""Handler for edit a comment"""
	
	@comment_exists
	@user_logged_in
	@user_owns_comment
	def get(self, post_id, post_user_id, comment_id):

		postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
		key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
		comment = db.get(key)

		self.render('editcomment.html', content=comment.content)

	@comment_exists
	@user_logged_in
	@user_owns_comment
	def post(self, post_id, post_user_id, comment_id):

		content = self.request.get('content')

		postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
		key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
		comment = db.get(key)

		comment.content = content
		comment.put()

		self.redirect('/' + post_id)
