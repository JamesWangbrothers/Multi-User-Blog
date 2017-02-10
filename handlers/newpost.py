from handlers.blog import BaseHandler
from models.post import Post
from helpers import *

class NewPost(BaseHandler):
	"""Handler for creating a new Post"""

	def get(self):
		# if user is login, go to newpost page
		if self.user:
			self.render("newpost.html")
		else:
			self.redirect("/login")

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content').replace('\n', '<br>')
		user_id = User.by_name(self.user.name)

		if self.user:
			if self.request.get("cancel"):
				self.redirect('/blog')

			if subject and content:
					p = Post(parent = blog_key(), subject = subject, content = content, user = user_id)
					p.put()
					self.redirect('/blog/%s' % str(p.key().id()))
			else:
				error = "subject and content, please!"
				self.render("newpost.html", subject = subject, content = content, error = error)
		else:
			self.redirect("/login")