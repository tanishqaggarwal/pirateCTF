import webapp2

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'html')))

class Index(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(jinja_environment.get_template('index.html').render())
		self.set_cookie("theflag?","on your quest for a recon problem? Part 1 of the flag is the_beginning_of_the_fun_")