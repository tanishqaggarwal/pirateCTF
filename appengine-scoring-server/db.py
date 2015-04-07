#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

from google.appengine.ext import ndb

from google.appengine.ext.db import EmailProperty
from google.appengine.ext.db import PostalAddressProperty
from google.appengine.ext.db import CategoryProperty
from google.appengine.ext.db import PhoneNumberProperty

class ProblemAttempts(ndb.Model):
	attempt    = ndb.StringProperty(required=True)
	explanation = ndb.TextProperty() #used to verify legit problem solves, since teams could just create duplicate accounts to harvest flags if no explanation was necessary. Can be disabled in main.py.
	time       = ndb.DateTimeProperty(required=True,auto_now_add=True)
	problem    = ndb.StringProperty() #reference problem titles
	ip         = ndb.StringProperty(required=True)
	user       = ndb.StringProperty(required=True) #username of user
	successful = ndb.BooleanProperty(required=True)
	buyed      = ndb.BooleanProperty(default=False)

class Teams(ndb.Model):
	teamname            = ndb.StringProperty(required=True)
	school              = ndb.StringProperty(required=True)
	points 			    = ndb.IntegerProperty(default=0)
	problems_attempted  = ndb.StructuredProperty(ProblemAttempts,repeated=True)
	successful_attempts = ndb.StructuredProperty(ProblemAttempts,repeated=True)
	adult_coordinator   = ndb.StringProperty(required=True)
	postal_address      = ndb.TextProperty(required=True)
	phone               = ndb.StringProperty(required=True)
	shell_username      = ndb.StringProperty(required=True)
	shell_password      = ndb.StringProperty(required=True)
	passphrase          = ndb.StringProperty(required=True)
	teamtype            = ndb.StringProperty(required=True)
	classname           = ndb.StringProperty(default="defaultclass")

class Classes(ndb.Model):
	classname                = ndb.StringProperty(required=True)
	classpassphrase          = ndb.StringProperty(required=True)
	classadult_email         = ndb.StringProperty(required=True)
	classadult_firstname     = ndb.StringProperty(required=True)
	classadult_lastname      = ndb.StringProperty(required=True)
	classadult_phonenumber   = ndb.StringProperty(required=True)
	classadult_postaladdress = ndb.TextProperty(required=True)
	class_school             = ndb.StringProperty(required=True)

class Users(ndb.Model):
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