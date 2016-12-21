import os, webapp2, jinja2

## my templates directory will be current directory I'm in, and slash templates.
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
## this is a new jinja enviornment
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	## takes template as the filename, and a bunch of extra parameters. '**'is the python syntax for python parameters
	def render_str(self, template, **params):
		t = jinja_env.get_template(template) ## tell jinja to load the template file
		return t.render(params) ## returns the string

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):
		items = self.request.get_all("food")
		self.render("shopping_list.html", items = items)

		# output = form_html
		# output_hidden = ""

		# items = self.request.get_all("food")
		# if items:
		# 	output_items = ""
		# 	for item in items:
		# 		output_hidden += hidden_html % item
		# 		output_items += item_html % item
		# 	output_shopping = shopping_list_html % output_items
		# 	output += output_shopping

		# output = output % hidden_html
		# self.write(output)

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)