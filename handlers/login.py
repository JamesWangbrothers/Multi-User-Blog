from handlers.blogbase import BaseHandler
from models.user import User

class Login(BaseHandler):
	"""Handler for user login"""
	
	def get(self):
		self.render('login.html')

	def post(self):
		self.username = self.request.get('username')
		self.password = self.request.get('password')

		if self.username and self.password:
			u = User.login(self.username, self.password)
			name = User.by_name(self.username)

			if u:
				self.login(u)
				self.redirect('/')
			elif not name:
				error = 'username not exists'
				self.render('login.html', error=error)
			else:
				error = 'incorrect password'
				self.render('login.html', error=error)	
		else:
			error = "please enter both username and password"
			self.render('login.html', error=error)