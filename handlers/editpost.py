from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from helpers import *

class EditPost(BaseHandler):
	"""Handles editing blog posts"""

	def get(self, post_id):
		# get the key for this post
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		
		# check if the user is logged in, and if this user is the author of this post
		if self.user and self.user.key().id() == post.user_id:
			# go to edite post page
			self.render("editpost.html", subject=post.subject, content=post.content, post_id=post_id)
		elif not self.user:
			self.redirect('/login')
		else:
			self.write("You can't edit this post!")

	def post(self, post_id):
		# get the key for this post
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if not self.user:
			self.redirect('/login')

		if self.user and self.user.key().id() == post.user_id:
			# get the subject, content and user id when the form is submitted
			subject = self.request.get("subject")
			content = self.request.get("content")

			if subject and content:
				key = db.Key.from_path('Post', int(post_id), parent=blog_key())
				post = db.get(key)

				post.subject = subject
				post.content = content

				post.put()

				self.redirect("/%s" % str(post.key().id()))
			else:
				error = "please enter both subject and content!"
				self.render("newpost.html", subject=subject, content=content, error=error)
		else:
			self.write("You are not authorized to edit this blog")
