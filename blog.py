import os, re, webapp2, jinja2, random, hashlib, hmac, time, codecs
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

secret = 'fart'

################### Global Helper Function ###########################

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

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	"""validate the username"""
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	"""validate the password"""
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	"""validate the email"""
	return not email or EMAIL_RE.match(email)

################### Base Handler for Convenience ###########################

class BaseHandler(webapp2.RequestHandler):

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

def render_post(response, post):
	response.out.write('<b>' + post.subject + '</br><br>')
	response.out.write(post.content)

############################# Rot13 ########################################

class Rot13(BaseHandler):
	def get(self):
		self.render("rot13.html")

	def post(self):
		rot13=""
		text = self.request.get("text")
		if text:
			rot13 = text.encode("rot13")

		self.render('rot13.html', text = rot13)

############################## Users ######################################

class User(db.Model):
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

############################# Signup ######################################

class Signup(BaseHandler):
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

	def done(self, *a, **kw):
		raise NotImplementedError

class Unit2Signup(Signup):
	def done(self):
		self.redirect('/unit2/welcome?username='  + self.username)


############################# Register ######################################

class Register(Signup):
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
			self.redirect('unit3/welcome')

############################# Login ######################################

class Login(BaseHandler):
	def get(self):
		self.render('login.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/unit3/welcome')
		else:
			msg = 'Invalid login'
			self.render('login.html', error = msg)

############################# Logout ######################################

class Logout(BaseHandler):
	def get(self):
		if self.user:
			self.logout()
			self.redirect('/blog')
		else:
			error = "Please log in first"
			self.render("login.html", error=error)

############################## Blog Setup ######################################

def blog_key(name = 'default'):
	"""define the blogs's parent"""
	return db.Key.from_path('Post', name)

class Post(db.Model):
	"""create a database to store blog posts"""
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	user = db.ReferenceProperty(User, required = True, collection_name="blogs")

	def render(self):
		"""show line breaks in blog content correctly when page is rendered"""
		self._render_text = self.content.replace('\n', '</br>')
		return render_str("permalink.html", post = self)

############################## Blog Main Page ######################################

class BlogMain(BaseHandler):
	"""Blog Main Page"""
	def get(self):
		# get all posts
		posts = Post.all().order('-created') ## db.GqlQuery("select * from Post order by created desc limit 10")
		if posts:
			self.render("front.html", posts = posts)

############################## Blog Post Page ######################################

class PostPage(BaseHandler):
	def get(self, post_id):
		# get key for from the blog
		key = db.Key.from_path('Post', int(post_id), parent = blog_key())
		post = db.get(key)

		# if the blog does not exist, show a 404 error
		if not post:
			self.error(404)
			return

		self.render("permalink.html", post = post)

	def post(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent = blog_key())
		post = db.get(key)
		user_id = User.by_name(self.user.name)

		if self.user:
			# check if the user clicks the edit
			if self.request.get("edit"):
				# check if the user is the author
				if post.user.key().id() == User.by_name(self.user.name).key().id():
					self.redirect('/blog/editpost/%s' % str(post.key().id()))
				else:
					error = "You are not authorized to edit this blog"
					self.render("permalink.html", post = post, error=error)
			
			# check if the user clicks the delte
			if self.request.get("delete"):
				if post.user.key().id() == User.by_name(self.user.name).key().id():
					db.delete(key)
					time.sleep(0.1)
					self.redirect('/blog')
				else:
					error = "You are not authorized to delete this blog"
					self.render("permalink.html", post = post, error=error)
		else:
			self.redirect("/login")

class NewPage(BaseHandler):
	def get(self):
		# if user is login, go to newpost page
		if self.user:
			self.render("newpost.html")
		else:
			self.redirect("/login")

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content').replace('\n', '<br>')
		user_id = User.by_name(self.user.name)

		if subject and content:
			p = Post(parent = blog_key(), subject = subject, content = content, user=user_id)
			p.put()
			self.redirect('/blog/%s' % str(p.key().id()))
		else:
			error = "subject and content, please!"
			self.render("newpost.html", subject = subject, content = content, error = error)

# class DeletePost(BaseHandler):
# 	""" Handles deletion of blog posts"""
# 	def get(self, post_id):
# 		if self.user:	
# 			key = db.Key.from_path('Post', int(post_id), parent = blog_key())
# 			post = db.get(key)
# 			if not post:
# 				self.error(404)
# 				return
# 			self.redirect("deletepost.html", post = post)
# 		else:
# 			self.redirect("/login")

# 	def post(self, post_id):
# 		key = db.Key.from_path('Post', int(post_id), parent = blog_key())
# 		post = db.get(key)
# 		if post:
# 			key.delete()
# 			time.sleep(0.1)
# 		self.redirect("/blog")

class EditPost(BaseHandler):
	"""Handles editing blog posts"""
	def get(self, post_id):
		# get the key for this post
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		
		# check if the user is logged in
		if self.user:
			# check if this user is the author of this post
			if post.user.key().id() == User.by_name(self.user.name).key().id():
				# go to edite post page
				self.render("editpost.html", post=post)
			else:
				self.response.out.write("You can't edit this post")
		else:
			self.redirect('/login')

	def post(self, post_id):
		# get the key for this post
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if self.request.get("update"):

			# get the subject, content and user id when the form is submitted
			subject = self.request.get("subject")
			content = self.request.get("content").replace('\n', '<br>')

			if post.user.key().id() == User.by_name(self.user.name).key().id():
				# update the blog post and redirect to the post page
				if subject and content:
					post.subject = subject
					post.content = content
					post.put()
					time.sleep(0.1)
					self.redirect("/blog/%s" % str(post.key().id()))
				else:
					error = "please enter both subject and content"
					self.render("editpost.html", subject = subject, content = content, error = error)
			else:
				self.response.out.write("You are not authorized to edit this blog")
		elif self.request.get("cancel"):
			self.redirect('/blog/%s' % str(post.key().id()))

########################### Welcome Pages ###################################
class Unit3Welcome(BaseHandler):
	def get(self):
		if self.user:
			self.render('welcome.html', username = self.user.name)
		else:
			self.redirect('/signup')

class Welcome(BaseHandler):
	def get(self):
		username = self.request.get('username')
		if valid_username(username):
			self.render('welcome.html', username = username)
		else:
			self.redirect('signup')

class MainPage(BaseHandler):
	def get(self):
		self.write('Hello, Udacity! It is a happy learning!')

app = webapp2.WSGIApplication([('/unit2/rot13', Rot13), 
							   ('/unit2/signup', Unit2Signup), 
							   ('/unit2/welcome', Welcome),
							   ('/unit3/welcome', Unit3Welcome),
							   ('/blog/?', BlogMain),
							   ('/blog/([0-9]+)',PostPage),
							   ('/blog/newpost', NewPage),
							   ('/blog/editpost/([0-9]+)', EditPost),
							   ('/signup', Register),
							   ('/login', Login),
							   ('/logout', Logout),
							   ('/', MainPage)
							   ], debug=True)



