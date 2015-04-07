#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

import webapp2
import jinja2
import os
import json
from db import *
from securefunctions import *
from google.appengine.api import memcache
from google.appengine.ext import ndb
import datetime
import marshal

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'html')))

class AdminConsole(webapp2.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			template = jinja_environment.get_template("adminconsole.html")
			self.response.out.write(template.render({}))

class AdminConsoleAddProblem(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "addproblem":
				form_dictionary = {
					"title" : self.request.get("title"),
					"text" : self.request.get("text"),
					"hint" : self.request.get("hint"),
					"flag" : self.request.get("flag"),
					"points" : self.request.get("points"),
					"problem_type" : self.request.get("problem_type"),
					"graderfunction" : self.request.get("graderfunction")
				}
				if not bool([formfield for formfield in formdictionary.values() if not formfield]):
					self.response.out.write("all form fields not completed")
					return
				
				form_dictionary['problem_type'] = form_dictionary['problem_type']

				problemquery = ndb.gql("SELECT * FROM Problems WHERE title = :titl OR text = :tex OR hint = :hin OR flag = :fla OR graderfunction = :grdrfunc",titl = form_dictionary['title'], tex = form_dictionary['text'], hin = form_dictionary['hint'], fla = form_dictionary['flag'], grdrfunc = form_dictionary['graderfunction']).get()

				if not problemquery:
					newproblem = Problems()
					for formfield, formvalue in form_dictionary.items():
						setattr(newproblem,formfield,formvalue)
					newproblem.put()
					self.response.out.write("problem added")
				else:
					self.response.out.write("problem with same title or text already exists")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleAddUpdate(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "addupdate":
				form_dictionary = {
					"title" : self.request.get("title"),
					"update" : self.request.get("update"),
				}
				if not bool([formfield for formfield in formdictionary.values() if not formfield]):
					self.response.out.write("all form fields not completed")
					return

				form_dictionary['time'] = datetime.datetime.now()

				updatequery = ndb.gql("SELECT * FROM Updates WHERE title = :titl",titl = form_dictionary['title']).get()
				if not updatequery:
					newupdate = Updates()
					for formfield, formvalue in form_dictionary.items():
						setattr(newupdate,formfield,formvalue)
					newupdate.put()
					self.response.out.write("update added")
				else:
					self.response.out.write("update with same title already exists")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleRemoveProblem(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "removeproblem":
				self.response.out.write("problem removed")
				#make sure to update everyone's point values and problem attempts accordingly!
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleClearMemcache(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "clearmemcache":
				self.response.out.write("memcache cleared")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeFlag(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "changeflag":
				self.response.out.write("flag changed")
				#make sure to update everyone's problem solveds, points and problem attempts accordingly!
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeGraderFunction(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "changegraderfunction":
				self.response.out.write("problem grader function changed")
				#make sure to update everyone's problem solveds and point values and problem attempts accordingly!
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeProblemPointBuyValue(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "changeproblembuypointvalue":
				self.response.out.write("problem purchase point value changed")
				#make sure to update everyone's point values and problem attempts accordingly!
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeProblemActualPointValue(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "changeproblemactualpointvalue":
				self.response.out.write("problem point value changed")
				#make sure to update everyone's point values and problem attempts accordingly!
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeProblemChildren(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
			if not self.app.config("problem_hierarchy"):
				self.response.out.write("hierarchy not enabled")
				return
            if mode == "changeproblemchildren":
				self.response.out.write("problem children changed")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeProblemParents(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
			if not self.app.config("problem_hierarchy"):
				self.response.out.write("hierarchy not enabled")
				return
            if mode == "changeproblemparents":
				self.response.out.write("problem parents changed")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleRemoveTeam(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "removeteam":
				self.response.out.write("team removed")
				#make sure to autoremove users from the team!
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleAddTeam(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "addteam":
				form_dictionary = {
					"teamname" : self.request.get("teamname"),
					"school" : self.request.get("school"),
					"passphrase" : self.request.get("passphrase"),
					"adult_coordinator" : self.request.get("adult_coordinator"),
					"address_line1" : self.request.get("address_line1"),
					"city" : self.request.get("city"),
					"state" : self.request.get("state"),
					"zipcode" : self.request.get("zipcode"),
					"phone" : self.request.get("phone"),
					"teamtype" : self.request.get("teamtype"),
				}

				if not bool([formfield for formfield in formdictionary.values() if not formfield]):
					self.response.out.write("all form fields not completed")
					return

				form_dictionary['adult_coordinator'] = form_dictionary['adult_coordinator']
				form_dictionary['postal_address']    = self.request.get("address_line1") + "\n" + self.request.get("address_line2") + "\n" + self.request.get("city") + ", " + self.request.get("state") + " " + self.request.get("zipcode")
				form_dictionary['phone']             = form_dictionary['phone']
				form_dictionary['teamtype']          = form_dictionary['teamtype']

				form_dictionary.pop("address_line1")
				form_dictionary.pop("city")
				form_dictionary.pop("state")
				form_dictionary.pop("zipcode")

				classname       = ""
				classpassphrase = ""
				if self.request.get("classname"):
					classname       = self.request.get("classname")
					classpassphrase = self.request.get("classpassphrase")
					classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn AND classpassphrase = :classp",classn=classname,classp=classpassphrase).get()
					if not classquery:
						self.response.out.write("class not found")
						return
					else:
						form_dictionary['classname'] = classname
				else:
					form_dictionary['classname'] = "defaultclass"
				
				#check if team doesn't already exist
				teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn OR passphrase = :passphr",teamn=teamname, passphr=passphrase).get()
				if teamquery:
					self.response.out.write("team name or passphrase already taken")
				else:
					teamobject = Teams()
					
					for formfield, formvalue in form_dictionary.items():
						setattr(teamobject,formfield,formvalue)

					shellrequest = urllib2.Request("https://" + DOMAIN_NAME + ":" + SHELL_CREATION_PORT + "/createshell")
					shellrequest.add_data(urllib.encode({
						"teamname" : encrypt(return_pass_hash_secret() + teamname),
						}))
					self.response.out.write("submitting shell account creation request")
					shellinfo = json.loads(urllib2.urlopen(shellrequest).read())
					teamobject.shell_username = shellinfo.shell_username
					teamobject.shell_password = shellinfo.shell_password
					teamobject.put()

					self.response.out.write("team added")
					return
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleChangeTeamScore(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "changeteamscore":
				form_dictionary = {
					"team" : self.request.get("team"),
					"score" : self.request.get("score"),
				}
				if not bool([formfield for formfield in formdictionary.values() if not formfield]):
					self.response.out.write("all form fields not completed")
					return

				teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn=form_dictionary['team']).get()
				if teamquery:
					teamquery.points = form_dictionary['score']
					teamquery.put()
					self.response.out.write("team score changed")
				else:
					self.response.out.write("no team found")
					return
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleAddTeamMember(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "addteammember":
				form_dictionary = {
					"username" : self.request.get("username"),
					"teamname" : self.request.get("teamname"),
				}
				if not bool([formfield for formfield in formdictionary.values() if not formfield]):
					self.response.out.write("all form fields not completed")
					return

				userquery = ndb.gql("SELECT * FROM Users WHERE username = :usrn",usrn = form_dictionary['username']).get()
				teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = form_dictionary['teamname']).get()
				if not teamquery or not userquery:
					self.response.out.write("user or team not found")
					return					
				else:
					userquery.teamname = teamname
					userquery.put()
					self.response.out.write("user added to team")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleRemoveTeamMemberRemoveUser(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "removeteammember" or mode == "removeuser":
				username = self.request.get("username")
				userquery = ndb.gql("SELECT * FROM Users WHERE username = :usrn",usrn = username).get()
				if not userquery:
					self.response.out.write("user not found")
					return
				else:
					#delete user
					self.response.out.write("user removed")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleRemoveClass(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "removeclass":
				classname = self.request.get("classname")
				classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn", classn = classname).get()
				if not classquery:
					self.response.out.write("class not found")
					return
				else:
					for aclass in classquery:
						aclass.key.delete()
					userquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn", classn = classname).fetch(limit=None)
					for auser in userquery:
						auser.classname = "defaultclass"
						auser.put()
					self.response.out.write("class removed")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleAddClass(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "addclass":
				formdictionary = {
				"classname" : self.request.get("classname"),
				"classadult_school" : self.request.get("classadult_school"),
				"classpassphrase" : self.request.get("classpassphrase"),
				"classadult_email" : self.request.get("classadult_email"),
				"classadult_addressline1" : self.request.get("classadult_addressline1"),
				"classadult_city" : self.request.get("classadult_city"),
				"classadult_state" : self.request.get("classadult_state"),
				"classadult_zipcode" : self.request.get("classadult_zipcode"),
				"classadult_phonenumber" : self.request.get("classadult_phonenumber"),
				}

				if not bool([formfield for formfield in formdictionary.values() if not formfield]):
					self.response.out.write("all required form fields not completed")
					return

				form_dictionary['classadult_email']          = form_dictionary['classadult_email']
				form_dictionary['classadult_postal_address'] = form_dictionary['classadult_addressline1'] + "\n" + self.request.get("classadult_addressline2") + "\n" + form_dictionary['classadult_city'] + ", " + form_dictionary['classadult_state'] + " " + form_dictionary['classadult_zipcode']
				form_dictionary['classadult_phonenumber']    = form_dictionary['classadult_phonenumber']
				form_dictionary.pop("classadult_addressline1")
				form_dictionary.pop("classadult_city")
				form_dictionary.pop("classadult_state")
				form_dictionary.pop("classadult_zipcode")

				#check if class doesn't already exist
				classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn OR classpassphrase = :classpassphr",classn=classname, classpassphr=classpassphrase).fetch(limit=None)
				exists = False
				for anyclass in classquery:
					exists = True
				if not exists:
					newclass = Classes()
					
					for formfield, formvalue in form_dictionary.items():
						setattr(newclass,formfield,formvalue)

					newclass.put()

					self.response.out.write("class added")
				else:
					self.response.out.write("class name or passphrase already taken")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")
				
class AdminConsoleAddClassTeams(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():	
			mode = self.request.get("mode")
            if mode == "addclassteams":
				form_dictionary = {
					"teamname" : self.request.get("teamname"),
					"classname" : self.request.get("classname")
				}
				teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = form_dictionary['teamname']).get()
				if not teamquery:
					self.response.out.write("team not found")
					return
				else:
					classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn", classn = form_dictionary['classname']).get()
					if not classquery:
						self.response.out.write("class not found")
						return
					else:
						for team in teamquery:
							team.classname = classname
							team.put()
						self.response.out.write("team added to class")
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

class AdminConsoleRemoveClassTeams(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin():
			mode = self.request.get("mode")
            if mode == "removeclassteams":
				self.response.out.write("team removed from class")
				#update the class's scoreboard accordingly
			else:
				self.response.out.write("invalid mode")
		else:
			self.response.out.write("not logged in as admin")

#================INFORMATION REQUEST HANDLERS=======================#

class AdminConsoleInformationRequestTeamMembers(webapp2.RequestHandler):
	if users.is_current_user_admin():
		mode = self.request.get("mode")
		if mode == "requestteammembers":
			self.response.out.write("team members")
		else:
			self.response.out.write("invalid mode")
	else:
		self.response.out.write("not logged in as admin")

class AdminConsoleInformationRequestClassTeams(webapp2.RequestHandler):
	if users.is_current_user_admin():
		mode = self.request.get("mode")
        if mode == "requestclassteams":
			self.response.out.write("class teams")
		else:
			self.response.out.write("invalid mode")
	else:
		self.response.out.write("not logged in as admin")

class AdminConsoleInformationRequestClassTeams(webapp2.RequestHandler):
	if users.is_current_user_admin():
		mode = self.request.get("mode")
        if mode == "requestalldata":
			pass
		else:
			self.response.out.write("invalid mode")
	else:
		self.response.out.write("not logged in as admin")
