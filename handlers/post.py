from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from helpers import *
from decorators import *

class PostPage(BaseHandler):
	"""The Blog Main page Handler"""
	
	@post_exists
	def get(self, post_id):
		# get key for from the blog
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		comments = db.GqlQuery("select * from Comment where ancestor is :1 order by created desc limit 10", key)

		self.render("permalink.html", post=post, comments=comments)