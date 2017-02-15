from handlers.blogbase import BaseHandler
from models.post import Post
from decorators import *

class NewPost(BaseHandler):
	"""Handler for creating a new Post"""

	@user_logged_in
	def get(self):

		self.render('newpost.html')

	@user_logged_in
	def post(self):
		
		subject = self.request.get('subject')
		content = self.request.get('content').replace('\n', '<br>')

		if subject and content:
			p = Post(parent=blog_key(), subject=subject, content=content, user_id=self.user.key().id())
			p.put()
			self.redirect('/%s' % str(p.key().id()))
		else:
			error = 'enter subject and content, please!'
			self.render("newpost.html", subject=subject, content=content, error=error)
