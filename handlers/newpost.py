from handlers.blogbase import BaseHandler
from models.post import Post
from helpers import *

class NewPost(BaseHandler):
	"""Handler for creating a new Post"""

	def get(self):
		# if user is login, go to newpost page
		if self.user:
			self.render("newpost.html")
		else:
			error="you must login first"
			self.render("base.html", access_error=error)

	# @user_logged_in
	def post(self):
		if not self.user:
		 	return self.redirect('/login')
		
		subject = self.request.get('subject')
		content = self.request.get('content').replace('\n', '<br>')

		if subject and content:
			p = Post(parent=blog_key(), subject=subject, content=content, user_id=self.user.key().id())
			p.put()
			self.redirect('/%s' % str(p.key().id()))
		else:
			error = "enter subject and content, please!"
			self.render("newpost.html", subject=subject, content=content, error=error)
