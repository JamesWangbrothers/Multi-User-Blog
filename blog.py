import os, re, webapp2, jinja2, random, hashlib, hmac, time, codecs
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

secret = 'fart'

################### Global Helper Function ###########################

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
			self.redirect('/welcome')

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
			self.redirect('/welcome')
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

############################## Blog Database Setup ######################################

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
		return render_str("post.html", post = self)

class Like(db.Model):
	"""create a database to store likes"""
	post = db.ReferenceProperty(Post, required=True)
	user = db.ReferenceProperty(User, required=True)

	@classmethod
	def by_blog_id(cls, blog_id):
		"""get number of likes from a blog with its blog id"""
		l = Like.all().filter('post =', blog_id)
		return l.count()

	@classmethod
	def check_like(cls, blog_id, user_id):
		"""get number of likes from its blog id and user id"""
		cl = Like.all().filter(
		    'post =', blog_id).filter('user =', user_id)
		return cl.count()

class Dislike(db.Model):
	"""create a database to store all dislikes"""
	post = db.ReferenceProperty(Post, required=True)
	user = db.ReferenceProperty(User, required=True)

	@classmethod
	def by_blog_id(cls, blog_id):
		"""get number of dislikes from a blog with its blog id"""
		ul = Dislike.all().filter('post =', blog_id)
		return ul.count()

	@classmethod
	def check_dislike(cls, blog_id, user_id):
		"""get number of dislikes from its blog id and user id"""
		cul = Dislike.all().filter(
		    'post =', blog_id).filter(
		    'user =', user_id)
		return cul.count()

class Comment(db.Model):
	"""create a database to store all comments"""
	post = db.ReferenceProperty(Post, required=True)
	user = db.ReferenceProperty(User, required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	text = db.TextProperty(required=True)

	@classmethod
	def count_by_blog_id(cls, blog_id):
		"""get number of comments for a blog id"""
		c = Comment.all().filter('post=', blog_id)
		return c.count()

	@classmethod
	def all_by_blog_id(cls, blog_id):
		"""get all comments from a specific blog with its blog id"""
		c = Comment.all().filter('post =', blog_id).order('created')
		return c

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

		likes = Like.by_blog_id(post)
		dislikes = Dislike.by_blog_id(post)

		comments = Comment.all_by_blog_id(post)
		comments_count = Comment.count_by_blog_id(post)

		self.render("post.html", post = post, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)

	def post(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent = blog_key())
		post = db.get(key)
		user_id = User.by_name(self.user.name)

		likes = Like.by_blog_id(post)
		dislikes = Dislike.by_blog_id(post)
		liked = Like.check_like(post, user_id)
		disliked = Dislike.check_dislike(post, user_id)

		comments = Comment.all_by_blog_id(post)
		comments_count = Comment.count_by_blog_id(post)

		if self.user:
			# check if the user clicks the edit
			if self.request.get("edit"):
				# check if the user is the author
				if post.user.key().id() == User.by_name(self.user.name).key().id():
					self.redirect('/blog/editpost/%s' % str(post.key().id()))
				else:
					error = "You are not authorized to edit this blog"
					self.render("post.html", post = post, error = error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)
			
			# check if the user clicks the delete
			if self.request.get("delete"):
				if post.user.key().id() == User.by_name(self.user.name).key().id():
					self.redirect('/blog/deletepost/%s' % str(post.key().id()))
				else:
					error = "You are not authorized to delete this blog"
					self.render("post.html", post = post, error = error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)

			# check if the user clicks the like
			if self.request.get("like"):
				# check if the user is trying to like its own blog
				if post.user.key().id() != User.by_name(self.user.name).key().id():
					# check the user is already liked or disliked the page, if no, add a like to the database
					if liked == 0:
						l = Like(post = post, user = User.by_name(self.user.name))
						l.put()
						time.sleep(0.1)
						self.redirect('/blog/%s' % str(post.key().id()))
					else:
						error = "You have already like this blog"
						self.render("post.html", post = post, error = error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)
				else:
					error = "You can't like your own blogs"
					self.render("post.html", post = post, error = error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)
					# check if the user clicks the like
			
			if self.request.get("dislike"):
				# check if the user is trying to like its own blog
				if post.user.key().id() != User.by_name(self.user.name).key().id():
					# check the user is already liked or disliked the page, if no, add a like to the database
					if disliked == 0:
						dl = Dislike(post = post, user = User.by_name(self.user.name))
						dl.put()
						time.sleep(0.1)
						self.redirect('/blog/%s' % str(post.key().id()))
					else:
						error = "You have already dislike this blog"
						self.render("post.html", post = post, error = error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)
				else:
					error = "You can't dislike your own blogs"
					self.render("post.html", post = post, error = error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)
			
			if self.request.get("add_comment"):
				comment_text = self.request.get("comment_text")
				if comment_text:
					c = Comment(post = post, user = User.by_name(self.user.name), text = comment_text)
					c.put()
					time.sleep(0.1)
					self.redirect('/blog/%s' % str(post.key().id()))
				else:
					comment_error = "Please write your comment"
					self.render("post.html", post = post, comment_error = comment_error, likes = likes, dislikes = dislikes, comments = comments, comments_count = comments_count)
		
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

class DeletePost(BaseHandler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if self.user:
			if post.user.key().id() == User.by_name(self.user.name).key().id():
				# go to edite post page
				self.render("deletepost.html")
			else:
				self.response.out.write("You can't delete this post")
		else:
			self.redirect('/login')

	def post(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		if self.request.get("delete"):
			db.delete(key)
			time.sleep(0.1)
			self.redirect('/blog')
		elif self.request.get("cancel"):
			self.redirect('/blog/%s' % str(post.key().id()))

class EditComment(BaseHandler):
	def get(self, post_id, comment_id):
		post = Post.get_by_id(int(post_id), parent = blog_key())
		comment = Comment.get_by_id(int(comment_id))

		if comment:
			if comment.user.name == self.user.name:
				self.render("editcomment.html", comment_text = comment.text)
			else:
				error = "You can't edit other user's comment"
				self.render("editcomment.html", error = error)
		else:
			error = "No comments for this post, yet"
			self.render("editcomment.html", error = error)

	def post(self, post_id, comment_id):
		if self.request.get("update_comment"):
			comment = Comment.get_by_id(int(comment_id))
			# check if this user is the author
			if comment.user.name == self.user.name:
				comment.text = self.request.get("comment_text")
				comment.put()
				time.sleep(0.1)
				self.redirect("/blog/%s" % str(post_id))
			else:
				error = "You can't edit other user's comment"
				self.render("editcomment.html", comment_text = comment_text, error = error)
		elif self.request.get("cancel"):
			self.redirect('/blog/%s' % str(post_id))

class DeleteComment(BaseHandler):
	def get(self, post_id, comment_id):
		comment = Comment.get_by_id(int(comment_id))

		if comment:
			if comment.user.name == self.user.name:
				db.delete(comment)
				time.sleep(0.1)
				self.redirect('/blog')
			else:
				self.write("You can't delete a comment from others")
		else:
			self.write("This comment was no longer exists")

########################### Welcome Pages ###################################

class Welcome(BaseHandler):
	def get(self):
		if self.user:
			self.render('welcome.html', username = self.user.name)
		else:
			self.redirect('/signup')

app = webapp2.WSGIApplication([('/', BlogMain),
							   ('/blog/?', BlogMain),
							   ('/welcome', Welcome),
							   ('/signup', Register),
							   ('/login', Login),
							   ('/logout', Logout),  
							   ('/blog/([0-9]+)',PostPage),
							   ('/blog/newpost', NewPage),
							   ('/blog/editpost/([0-9]+)', EditPost),
							   ('/blog/deletepost/([0-9]+)', DeletePost),
							   ('/blog/([0-9]+)/editcomment/([0-9]+)', EditComment),
							   ('/blog/([0-9]+)/deletecomment/([0-9]+)', DeleteComment)
							   ], debug=True)




