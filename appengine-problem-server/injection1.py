from google.appengine.api import ndb
import webapp2

FLAG = "ez_pz_injection"
PREVIOUS_FLAGS = ["something"]

class InjectionOne(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(jinja_environment.get_template("problems/injection1/login.html").render({}))
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		userquery = ndb.gql("SELECT * FROM Users WHERE username = " + username + " AND password = " + password).get()
		if userquery:
			self.response.out.write(jinja_environment.get_template("problems/injection1/admin.html").render({}))
		else:
			self.response.out.write(jinja_environment.get_template("problems/injection1/loginfail.html").render({}))

#When you get to the admin page, this class spits out the flag when a previous flag is entered on the admin page.
class InjectionOneAdmin(webapp2.RequestHandler):
	def post(self):
		flag = self.request.get("flag")
		if flag in PREVIOUS_FLAGS:
			self.response.out.write(FLAG)
		else:
			self.response.out.write("invalid flag")