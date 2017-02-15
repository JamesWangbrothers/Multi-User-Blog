from helpers import *

def user_logged_in(function):
	@wraps(function)
	def wrapper(self, *args, **kwargs):
		if not self.user:
			error = "please login first"
			self.render("login.html", error=error)
		else:
			return function(self, *args, **kwargs)
	return wrapper

def post_exists(function):
	@wraps(function)
	def wrapper(self, post_id, *args):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		if not post:
			self.error(404)
		else:
			return function(self, post_id, *args)
	return wrapper

def comment_exists(function):
	@wraps(function)
	def wrapper(self, post_id, post_user_id, comment_id):
		postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
		comment_key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
		comment = db.get(comment_key)
		if not comment:
			self.error(404)
		else:
			return function(self, post_id, post_user_id, comment_id)
	return wrapper

def user_owns_post(function):
	@wraps(function)
	def wrapper(self, post_id, *args):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if self.user.key().id() != post.user_id:
			error = "you don't have permission for this post!"
			comments = db.GqlQuery("select * from Comment where ancestor is :1 order by created desc limit 10", key)	
			self.render("permalink.html", post=post, comments=comments, error=error)
		else:
			return function(self, post_id, *args)
	return wrapper

def user_not_owns_post(function):
	@wraps(function)
	def wrapper(self, post_id, *args):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if self.user.key().id() == post.user_id:
			error = "Sorry, you can not like or dislike your own post"	
			self.render('permalink.html', post=post, error=error)
		else:
			return function(self, post_id, *args)
	return wrapper

def user_owns_comment(function):
	@wraps(function)
	def wrapper(self, post_id, post_user_id, comment_id):
		postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
		comment_key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
		comment = db.get(comment_key)

		if self.user.key().id() != int(post_user_id):
			error = "you can't edit or delete your own comment!"
			self.render("front.html", error=error)
		else:
			return function(self, post_id, post_user_id, comment_id)
	return wrapper