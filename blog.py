from webapp2 import WSGIApplication
from google.appengine.ext import db
from helpers import *

# Models
from models.user import User
from models.post import Post
from models.like import Like
from models.comment import Comment

# Handlers
from handlers.blogbase import BaseHandler
from handlers.blogfront import BlogMain
from handlers.signup import Signup
from handlers.login import Login
from handlers.logout import Logout
from handlers.post import PostPage
from handlers.newpost import NewPost
from handlers.editpost import EditPost
from handlers.deletepost import DeletePost
from handlers.likepost import LikePost
from handlers.unlikepost import UnlikePost
from handlers.addcomment import AddComment
from handlers.editcomment import EditComment
from handlers.deletecomment import DeleteComment

app = webapp2.WSGIApplication([('/', BlogMain),
							   ('/signup', Signup),
							   ('/login', Login),
							   ('/logout', Logout),  
							   ('/([0-9]+)',PostPage),
							   ('/newpost', NewPost),
							   ('/([0-9]+)/edit', EditPost),
							   ('/([0-9]+)/delete/([0-9]+)', DeletePost),
							   ('/([0-9]+)/addcomment/([0-9]+)', AddComment),
							   ('/([0-9]+)/([0-9]+)/editcomment/([0-9]+)', EditComment),
							   ('/([0-9]+)/([0-9]+)/deletecomment/([0-9]+)', DeleteComment),
							   ('/([0-9]+)/like', LikePost),
							   ('/([0-9]+)/unlike', UnlikePost)
							   ], debug = True)




