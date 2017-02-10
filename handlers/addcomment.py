from google.appengine.ext import db
from handlers.blog import BaseHandler
from helpers import *
from models.comment import Comment

class AddComment(BaseHandler):
	def get(self, post_id, user_id):
		if not self.user:
			self.redirect('/login')
		else:
			self.render("/addcomment.html")

	def post(self, post_id, user_id):
		if not self.user:
			return 

		content = self.request.get('content')
		user_name = self.user.name
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())

		c = Comment(parent=key, user_id=int(user_id), content=content, user_name=user_name)
		c.put()

		self.redirect('/' + post_id)