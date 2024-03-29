#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

from google.appengine.ext import ndb
import datetime

class ProblemAttempts(ndb.Model):
	attempt    = ndb.StringProperty(required=True)
	explanation = ndb.TextProperty() #used to verify legit problem solves, since teams could just create duplicate accounts to harvest flags if no explanation was necessary. Can be disabled in main.py.
	time       = ndb.DateTimeProperty(auto_now_add=True)
	problem    = ndb.StringProperty() #reference problem titles
	ip         = ndb.StringProperty(required=True)
	user       = ndb.StringProperty(required=True) #username of user
	successful = ndb.BooleanProperty(required=True)
	buyed      = ndb.BooleanProperty(default=False)

class Teams(ndb.Model):
	created             = ndb.DateTimeProperty(auto_now_add=True)
	teamname            = ndb.StringProperty(required=True)
	school              = ndb.StringProperty(required=True)
	points 			    = ndb.IntegerProperty(default=0)
	problems_attempted  = ndb.StructuredProperty(ProblemAttempts,repeated=True)
	successful_attempts = ndb.StructuredProperty(ProblemAttempts,repeated=True)
	last_successful     = ndb.DateTimeProperty(default=datetime.datetime(1900,1,1,0,0,0,0))
	adult_coordinator   = ndb.StringProperty(required=True)
	postal_address      = ndb.TextProperty(required=True)
	phone               = ndb.StringProperty(required=True)
	shell_username      = ndb.StringProperty(required=True)
	shell_password      = ndb.StringProperty(required=True)
	passphrase          = ndb.StringProperty(required=True)
	teamtype            = ndb.StringProperty(required=True,choices=["Competitive","Observer"])
	classname           = ndb.StringProperty(default="defaultclass")

class Users(ndb.Model):
	created   = ndb.DateTimeProperty(auto_now_add=True)
	user      = ndb.UserProperty(required=True)
	username  = ndb.StringProperty(required=True) #extracted from User object as the user's name
	teamname  = ndb.StringProperty(required=True) #reference team name
	classname = ndb.StringProperty(default="defaultclass") #reference class name

class Updates(ndb.Model):
	title  = ndb.StringProperty(required=True)
	update = ndb.TextProperty(required=True)
	time   = ndb.DateTimeProperty(auto_now_add=True)

class MicroUpdates(ndb.Model):
	title  = ndb.StringProperty(required=True)
	update = ndb.TextProperty(required=True)
	time   = ndb.DateTimeProperty(auto_now_add=True)

class Problems(ndb.Model):
	created   = ndb.DateTimeProperty(auto_now_add=True)
	title            = ndb.StringProperty(required=True)
	text             = ndb.TextProperty(required=True)
	number_solved    = ndb.IntegerProperty(default=0)
	flag             = ndb.StringProperty(required=True)
	hint             = ndb.TextProperty(required=True)
	points           = ndb.IntegerProperty(required=True)
	problem_type     = ndb.StringProperty(required=True,choices=["Forensics","Web Exploit","Binary Exploit","Reverse Engineering","Cryptography","Web Reconnaissance","Master Challenge","Algorithms"])
	graderfunction   = ndb.GenericProperty(required=True)
	buy_for_points   = ndb.IntegerProperty(required=True)
	problem_parents  = ndb.GenericProperty(repeated=True)
	problem_children = ndb.GenericProperty(repeated=True)