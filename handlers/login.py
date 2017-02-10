class Login(BaseHandler):
	"""Handler for user login"""
	def get(self):
		self.render('login.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/welcome')
		else:
			msg = 'Invalid login'
			self.render('login.html', error = msg)

		if self.request.get("cancel"):
			self.redirect('/blog')