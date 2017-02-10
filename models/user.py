from google.appengine.ext import db
from helpers import *

class User(db.Model):
	"""create User database"""
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls,uid):
		"""get user with user id"""
		return User.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, name):
		"""get user with  user name"""
		u = User.all().filter('name =', name).get()
		return u

	@classmethod
	def register(cls, name, pw, email = None):
		"""register by hashing the password first"""
		pw_hash = make_pw_hash(name, pw)
		return User(parent = users_key(), name = name, pw_hash = pw_hash, email = email)

	@classmethod
	def login(cls, name, pw):
		"""login by checking the password first"""
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u