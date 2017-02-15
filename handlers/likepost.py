from google.appengine.ext import db
from handlers.blogbase import BaseHandler
from models.like import Like
from decorators import *

class LikePost(BaseHandler):

    @post_exists
    @user_logged_in
    @user_not_owns_post
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        user_id = self.user.key().id()
        post_id = post.key().id()

        like = Like.all().filter('user_id =', user_id).filter('post_id =', post_id).get()

        if like:
            self.redirect('/' + str(post.key().id()))

        else:
            like = Like(parent=key, 
                        user_id=self.user.key().id(),
                        post_id=post.key().id())

            post.likes += 1

            like.put()
            post.put()

            self.redirect('/' + str(post.key().id()))

