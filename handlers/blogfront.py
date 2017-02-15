from google.appengine.ext import db
from handlers.blogbase import BaseHandler

class BlogMain(BaseHandler):
	"""Blog Main Page"""
	
	def get(self):
		# get all posts
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		count = posts.count()
		if posts:
			self.render("front.html", posts=posts, count=count)		