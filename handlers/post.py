from google.appengine.ext import db
from handlers.blog import BaseHandler
from helpers import *

class PostPage(BaseHandler):
	"""The Blog Main page Handler"""
	def get(self, post_id):
		# get key for from the blog
		key = db.Key.from_path('Post', int(post_id), parent = blog_key())
		post = db.get(key)

		# if the blog does not exist, show a 404 error
		if not post:
			self.error(404)
			return

		self.render("permalink.html", post=post, comments=comments)