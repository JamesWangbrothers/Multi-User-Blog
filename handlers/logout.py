from handlers.blogbase import BaseHandler

class Logout(BaseHandler):
	"""Handler for user logout"""
	
	def get(self):
		if self.user:
			self.logout()
			self.redirect('/')
		else:
			error = "Please log in first"
			self.render("login.html", error = error)