class Signup(BaseHandler):
	"""Handler for user to signup"""
	def get(self):
		self.render("signup.html")

	def post(self):
		have_error = False
		self.username = self.request.get("username")
		self.password = self.request.get("password")
		self.verify = self.request.get("verify")
		self.email = self.request.get("email")

		params = dict(username=self.username, password=self.password)

		if not valid_username(self.username):
			params["error_username"] = "Please enter a valid username."
			have_error = True

		if not valid_password(self.password):
			params["error_password"] = "Please enter a valid password."
			have_error = True
		elif self.password != self.verify:
			params["error_verify"] = "Your password didn't match."
			have_error = True

		if not valid_email(self.email):
			params["error_email"] = "That's not a valid email."
			have_error = True

		if have_error:
			self.render("signup.html", **params)
		else:
			self.done()

		if self.request.get("cancel"):
			self.redirect('/blog')

	def done(self, *a, **kw):
		raise NotImplementedError

class Register(Signup):
	"""Handler for new user to create an acount."""
	def done(self):
		# make sure the user doesn't already exist
		u = User.by_name(self.username)
		if u:
			msg = 'That user already exists.'
			self.render('signup.html', error_username = msg)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)
			self.redirect('/welcome')