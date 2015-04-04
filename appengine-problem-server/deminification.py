#PirateCTF 2015 AppEngine problem server.

import webapp2

FLAG = "hope_you_had_fun_deminifying"
PREVIOUS_FLAGS = ["something"]

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'html')))

class DeminificationExercise(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(jinja_environment.get_template('problems/deminification_exercise/deminification.html').render())

class RequestDeminificationFlag(webapp2.RequestHandler):
	def post(self):
		password = self.request.get("p") #should be the flag of the previous exercise
		if password in PREVIOUS_FLAGS:
			self.response.out.write(json.dumps({ "tf" : FLAG }))