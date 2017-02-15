from handlers.blogbase import BaseHandler
from helpers import *
from decorators import *

class Logout(BaseHandler):
	"""Handler for user logout"""
	
	@user_logged_in
	def get(self):
		self.logout()
		self.redirect('/')
