#PirateCTF 2015 AppEngine problem server.

import webapp2
import base64
import json

FLAG = "you_better_not_encrypt_your_stuff_like_this"
PREVIOUS_FLAGS = ["something"]

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'static/html')))

class FishyCookiesLogin(webapp2.RequestHandler):
	def get(self):
		if self.request.cookies.get('fishycookie'):
			fishycookie = json.loads(securefishfunction("encrypt",self.request.cookies.get('fishyfunction')))
			if fishycookie.level > 9000:
				self.redirect("/chondrichthyes_admin")
			else:
				self.redirect("/no_fish_for_you")
		else:
			self.response.out.write(jinja_environment.get_template("problems/fishycookies/login.html").render())
	def get(self):
		if self.request.cookies.get('fishycookie'):
			fishycookie = json.loads(securefishfunction("encrypt",self.request.cookies.get('fishycookie')))
			if fishycookie.level > 9000:
				self.redirect("/chondrichthyes_admin")
			else:
				self.redirect("/no_fish_for_you")
		else:
			self.set_cookie("fishycookie",securefishfunction("encrypt",json.dumps({ 
				"username" : self.request.get("username"),
				"userlevel" : 1,
			})))
			self.redirect("/no_fish_for_you")

class FishyCookiesAdmin(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(jinja_environment.get_template("problems/fishycookies/admin.html").render({ "flag" : FLAG }))

class FishyCookiesNoAdmin(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(jinja_environment.get_template("problems/fishycookies/noadmin.html").render({}))

class FishyCookiesEncryptionDecryption(webapp2.RequestHandler):
	def post(self):
		mode = self.request.get("mode")
		text = self.request.get("text")
		password = self.request.get("password")
		if json.loads(text).userlevel > 9000:
			if password in PREVIOUS_FLAGS:
				self.response.out.write(securefishfunction(mode,text))
			else:
				self.response.out.write("need previous flag too as \"password\" to encrypt an admin-level entity")
		else:
			self.response.out.write(securefishfunction(mode,text))

def securefishfunction(mode,text):
	if mode == "encrypt":
		pass
	elif mode == "decrypt":
		pass
	else:
		return "invalid mode"