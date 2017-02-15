from handlers.blogbase import BaseHandler
from models.user import User
from helpers import *

class Signup(BaseHandler):
	"""Handler for user to signup"""
	
	def get(self):
		self.render('signup.html')

	def post(self):
		have_error = False
		self.username = self.request.get('username')
		self.password = self.request.get('password')
		self.verify = self.request.get('verify')
		self.email = self.request.get('email')

		params = dict(username=self.username, password=self.password)
		
		if self.username and self.password and self.verify:

			if not valid_username(self.username):
				params['error'] = "Please enter a valid username."
				have_error = True

			if not valid_password(self.password):
				params['error'] = "Please enter a valid password."
				have_error = True

			elif self.password != self.verify:
				params['error'] = "Your password didn't match."
				have_error = True

			if not valid_email(self.email):
				params['error'] = "That's not a valid email."
				have_error = True

		else:
			params['error'] = "Please enter username, password and verify password to signup"
			have_error = True

		if have_error:
			self.render('signup.html', **params)
		else:
			self.done()

	def done(self, *a, **kw):
		u = User.by_name(self.username)

		if u:
			error = "user already exist"
			self.render('signup.html', error=error)

		else:
			u = User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)
			self.redirect('/')