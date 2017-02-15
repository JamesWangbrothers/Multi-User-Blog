import webapp2
from helpers import *
from models.user import User

class BaseHandler(webapp2.RequestHandler):
	"""Basic Handler for coding convenience"""

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw) 

	def render_str(self, template, **params):
		params['user'] = self.user
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		"""securely set the cookie"""
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie','%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		"""read the cookie"""
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		"""set a cookie when the user log in"""
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		"""reset the cookie when the user logs out"""
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		"""get the user from secure cookie when we initialize pages, check if the user is login or not"""
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))