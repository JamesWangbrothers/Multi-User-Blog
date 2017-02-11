from google.appengine.ext import db
from helpers import *
from handlers.blogbase import BaseHandler
from models.comment import Comment

class AddComment(BaseHandler):

	# @user_logged_in
	def get(self, post_id, user_id):
		if not self.user:
			self.redirect('/login')
		else:
			self.render("/addcomment.html")

	# @user_logged_in
	def post(self, post_id, user_id):
		if not self.user:
			return 

		content = self.request.get('content')
		if content:

			user_name = self.user.name
			key = db.Key.from_path('Post', int(post_id), parent=blog_key())

			c = Comment(parent=key, user_id=int(user_id), content=content, user_name=user_name)
			c.put()

			self.redirect('/' + post_id)
		else:
			error = "enter content, please!"
			self.render("addcomment.html", content=content, error=error)