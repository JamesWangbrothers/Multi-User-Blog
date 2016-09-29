#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
							   autoescape = True)

secret = 'fart'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# take a val and return with a hash val
def make_secure_val(val):
	return '%s|%s' % (val, hmac.new(secret,val).hexdigest()) 

# take a hash val, make sure it's valid
def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val

# Parent class for all Handlers
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
    	t = jinja_env.get_template(template)
    	return t.render(params)

    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))
    
    def set_secure_cookie(self, name, val):
    	# store the (val|hash) into the cookie
    	cookie_val = make_secure_val(val)
    	# didn't include the expire time here, the cookie will expired when we close the browser
    	self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val)) 

    def read_secure_cookie(self, name):
    	cookie_val = self.request.cookies.get(name)
    	# if the cookie exist and the cookie past the check_secure_val function, we return cookie val
    	return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
    	# user.key().id() is how you get the user's id in google appengine in datastore
    	self.set_secure_cookie('user_id', str(user.key().id())) 

    def logout(self):
    	# set cookie equals nothing and keep the same path
    	self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # Google App Engine is a function that called before every request.
    # so here check for the user cookie, which is called user_id
    # if it exist, store it in self.user the actual user object
    def initialize(self, *a, **kw):
    	webapp2.RequestHandler.initialize(self, *a, **kw)
    	uid = self.read_secure_cookie('user_id')
    	self.user = uid and User.by_id(int(uid))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, Welcome to my Page!')

##### user stuff ######
# make a string of 5 letters
def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

# make a password hash
def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	# this return is what we store in database
	return '%s,%s' % (salt, h)

# verify password
def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)

# create the ancestor element in the database used to store users
# pretend have a group in the future, which in current case we don't
def users_key(group = 'default'):
	return db.Key.from_path('users', group)

# User object stored in Database. db.Model makes it as a datastore object
class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()

	# "@classmethod" is decorator, it allows to call it on the User object
	# cls instead of self, refer to class User, not instances of Users like Spez, ryan...
	@classmethod
	def by_id(cls, uid):
		# get_by_id is built in datastore
		return User.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, name):
		# the same as select * from User where name = name
		# get() retrieve the first instance
		u = User.all().filter('name =', name).get()
		return u 

	# create the user object, but does not store in the database yet
	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = make_pw_hash(name, pw)
		return User(parent = users_key(), name = name, pw_hash = pw_hash, email = email)

	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u

###### blog stuff #####

# define the blog key for blog's parent. 
# when store things in datastore, they don't have to have a parent
# parent is usually a element, here we name it with a key doesn't even exist
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Post(db.Model):
	# list all the property or blog entry that the blog has
	subject = db.StringProperty(required = True)  # less than 500 char, can be index
	content = db.TextProperty(required = True)    # more than 500 char, can not be index, also can have newline
	created = db.DateTimeProperty(auto_now_add = True) # automatically made the property
	last_modified = db.DateTimeProperty(auto_now = True) # keep the datastore up to date

	def render(self):
		### replace new line with line breaks for users to type and displace
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self)

### for just "/blog"
class BlogFront(BlogHandler):
	def get(self):
		# lookup all the posts ordered by creation time
		# post = Post.all().order('-created') 
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render('front.html', posts = posts)

### for "/blog/(0-9)+"
class PostPage(BlogHandler):
	def get(self, post_id):
		# make a key
		key = db.Key.from_path('Post', int(post_id), parent = blog_key())
		post = db.get(key)

		if not post:
			self.error(404)
			return

		self.render("permalink.html", post = post)

class NewPost(BlogHandler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')

		if subject and content:
			p = Post(parent = blog_key(), subject = subject, content = content)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id())) # get a object id in datastore

		else:
			error = "subject and content, please!"
			self.render("newpost.html", subject = subject, content = content , error = error)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
	def get(self):
		self.render('signup.html')

	def post(self):
		have_error = False
		self.username = self.request.get('username')
		self.password = self.request.get('password')
		self.verify = self.request.get('verify')
		self.email = self.request.get('email')

		params = dict(username = self.username, email = self.email)

		if not valid_username(self.username):
			params['error_username'] = "That's not a valid username"
			have_error = True

		if not valid_password(self.password):
			params['error_password'] = "That's not a valid password"
			have_error = True

		elif self.password != self.verify:
			params['error_verify'] = "Your password didn't match"
			have_error = True

		if not valid_email(self.email):
			params['error_email'] = "That's not a valid email address"
			have_error = True

		if have_error:
			self.render("signup.html", **params)
		else:
			self.done()

	def done(self, *a, **kw):
		raise NotImplementedError

class Unit2Signup(Signup):
	def done(self):
		self.redirect('/unit2/welcome?username=' + self.username)

class Register(Signup):
	def done(self):
		# make sure the user doesn't already exist
		u = User.by_name(self.username)
		if u:
			msg = 'that user already exist'
			self.render('signup.html', error_username = msg)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put() # store in the database

			self.login(u)
			self.redirect('/welcome?username=' + self.username)

class Login(BlogHandler):
	def get(self):
		self.render('login.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('unit3/welcome')
		else:
			msg = "Invaid login"
			self.render('login.html', error = msg)

class Logout(BlogHandler):
	def get(self):
		self.logout()
		self.redirect('/blog')

class Unit3Welcome(BlogHandler):
	def get(self):
		if self.user:
			self.render('welcome.html', username = self.user.name)
		else:
			self.redirect('/signup')

class Welcome(BlogHandler):
	def get(self):
		username = self.request.get('username')
		if valid_username(username):
			self.render('welcome.html', username = username)
		else:
			self.render('unit2/signup')

app = webapp2.WSGIApplication([
	('/', MainPage),
    ('/blog/?', BlogFront),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', PostPage),
    ('/signup', Register),
    ('/login', Login),
    ('/logout', Logout),
    ('/welcome', Welcome),
    ('/unit2/signup', Unit2Signup),
    ('/unit3/welcome', Unit3Welcome)
], debug=True)
