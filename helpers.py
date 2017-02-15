import os 
import re
import webapp2
import jinja2
import random
import hashlib
import hmac
import codecs
import time
from string import letters
from functools import wraps, partial
from google.appengine.ext import db

# Jinja Template
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

secret = 'fart'

def blog_key(name = 'default'):
	"""the helper function defines the blogs's parent"""
	return db.Key.from_path('Post', name)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
	"""create a secure cookie values"""
	return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
	"""check secure cookie values"""
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val

def make_salt(length = 5):
	"""make a string of 5 letters"""
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	"""make a password hashed"""
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	"""validate password, make sure the hash from the database matches the new hash based on the users entered in """
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
	"""get the key from User table"""
	return db.Key.from_path('users', group)

def valid_username(username):
	"""validate the username"""
	USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	return username and USER_RE.match(username)

def valid_password(password):
	"""validate the password"""
	PASS_RE = re.compile(r"^.{3,20}$")
	return password and PASS_RE.match(password)

def valid_email(email):
	"""validate the email"""
	EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
	return not email or EMAIL_RE.match(email)

def user_logged_in(function):
	@wraps(function)
	def wrapper(self, *args, **params):
		if not self.user:
			self.redirect('/login')
		else:
			return function(self, *args, **params)
	return wrapper

def post_exists(function):
	@wraps(function)
	def wrapper(self, post_id, *args):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		print key
		if not post:
			self.error(404)
		else:
			return function(self, post_id, *args)
	return wrapper

def comment_exists(function):
	@wraps(function)
	def wrapper(self, post_id, comment_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		comment_key = db.Key.from_path('Comment', int(comment_id), parent=self.user.key())
		comment = db.get(comment_key)
		if not comment:
			self.error(404)
		else:
			return function(self, post_id, comment_id, comment)
	return wrapper

# def user_owns_post(function):
# 	@wraps(function)
# 	def wrapper(self, post_id):
# 		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
# 		post = db.get(key)
# 		author = post.user_id
# 		logged_in_user = self.user.key().id()
		
# 		if author != logged_in_user:
# 			error = "you can't edit this post!"
# 			self.render("front.html", error = error)
# 		else:
# 			return function(self, post_id)
# 	return wrapper

# def user_owns_comment(function):
# 	@wraps(function)
# 	def wrapper(self, post_id):
# 	    comment_key = db.Key.from_path('Comment', int(comment_id), parent=self.user.key())
#         comment = db.get(comment_key)
#         author = comment.user_id
#         logged_in_user = self.user.key().id()

#         if author != logged_in_user:
#         	error = "you can't edit this comment!"
#         	self.render("front.html", error = error)
#         else:
#         	return function(self, post_id, comment_id)
# 	return wrapper

