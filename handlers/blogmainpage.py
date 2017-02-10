from google.appengine.ext import db
from handlers.blog import BaseHandler

class BlogMain(BaseHandler):
	"""Blog Main Page"""
	def get(self):
		# get all posts
		posts = Post.all().order('-created') ## db.GqlQuery("select * from Post order by created desc limit 10")
		count = posts.count()
		if posts:
			self.render("home.html", posts = posts, count = count)