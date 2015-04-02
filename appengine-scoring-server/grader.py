#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

from db import *
from securefunctions import *
import json
from google.appengine.ext import ndb
from google.appengine.api import memcache
import datetime
import webapp2

import pickle

#To not burden the grader for having to check if someone already solved previous problems, write the problems in such a way that you actually need the output of a previous problem to solve the next one.
class Grader(webapp2.RequestHandler):
	def post(self):
		problem = self.request.get("problemidentifier")
		attempt = self.request.get("attempt")
		explanation = self.request.get("explanation")
		ipaddr  = self.request.remote_addr

		teamselect = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = userobject.teamname).get()
		problemattempts = []
		successfulproblemattempts = []
		if teamselect.length() < 1:
			self.response.out.write("invalid user object")
			return

		aproblem = ndb.gql("SELECT * FROM Problems WHERE title = :titl",titl=problem).get()
		if problemslist.length() < 1:
			self.response.out.write("not a valid problem identifier")
			return

		if not explanation:
			self.response.out.write("explanation required for flag submission")
			return
		else:
			problemdata = memcache.get(aproblem.title)
			if not problemdata:
				memcache.add(aproblem.title,aproblem)
				problemdata = memcache.get(aproblem.title)
			func = pickle.loads(aproblem.graderfunction)

			flagcorrect = (func(attempt) or attempt == problemdata.flag)
			if flagcorrect:
				problemattempts = teamselect.problems_attempted
				successfulproblemattempts = teamselect.successful_attempts
				for anyproblem in successfulproblemattempts:
					if anyproblem.problem == problem:
						self.response.out.write("already solved")
						return
					
				aproblem.num_solved += 1
				aproblem.put()									
				theproblem             = ProblemAttempts()
				theproblem.attempt     = attempt
				theproblem.time        = CURRENT_TIME
				theproblem.successful  = True
				theproblem.problem     = problem
				theproblem.explanation = explanation
				theproblem.ip          = ipaddr
				theproblem.user        = userobject.username
				problemattempts.append(theproblem)
				successfulproblemattempts.append(theproblem)

				teamselect.problems_attempted = problemattempts
				teamselect.points            += aproblem.points
				teamselect.put()
				self.response.out.write("solved")

				#Note, a lot of memcache should get cleared here
				memcache.delete('problemsforteam' + userobject.teamname)
				memcache.delete('showproblemsforteam' + userobject.teamname)
				memcache.delete('scoreboard')
				memcache.delete('accountfor' + userobject.username)
				memcache.delete("teaminfoforteam" + userobject.teamname)
			else:
				problemattempts = teamselect.problems_attempted
				for anyproblem in problemattempts:
					if anyproblem.problem == problem and anyproblem.attempt == attempt:
						self.response.out.write("already tried this")
				
				theproblem             = ProblemAttempts()
				theproblem.attempt     = attempt
				theproblem.successful  = False
				theproblem.problem     = problem
				theproblem.explanation = explanation
				theproblem.ip          = ipaddr
				theproblem.user        = user.username
				problemattempts.append(theproblem)

				teamselect.problems_attempted = problemattempts
				teamselect.put()
				self.response.out.write("incorrect")

class Buyer(webapp2.RequestHandler):
	def post(self):
		problem = self.request.get("problemidentifier")
		ipaddr  = self.request.remote_addr

		teamselect = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = user.teamname).get()
		problemattempts = []
		if teamselect.length() < 1:
			self.response.out.write("invalid user object")
			return

		problemslist = ndb.gql("SELECT * FROM Problems WHERE title = :titl",titl=problem).get()
		if problemslist.length() < 1:
			self.response.out.write("not a valid problem identifier")
			return
		else:
			for aproblem in problemslist:

				for anattempt in teamselect.problems_attempted:
					if anattempt.problem == problem and anattempt.buyed == True:
						self.response.out.write("already bought")
						return

				if aproblem.buy_for_points > teamselect.points:
					self.response.out.write("not enough points")
					return

				problemdata = memcache.get(aproblem.title)
				if not problemdata:
					memcache.add(aproblem.title,aproblem)
					problemdata = memcache.get(aproblem.title)
				theproblem             = ProblemAttempts()
				theproblem.attempt     = aproblem.flag
				theproblem.successful  = True
				theproblem.problem     = problem
				theproblem.explanation = "bought"
				theproblem.ip          = ipaddr
				theproblem.buyed       = True
				problemattempts.append(theproblem)

				teamselect.problems_attempted = problemattempts
				teamselect.points -= aproblem.buy_for_points
				teamselect.put()
				self.response.out.write("bought")
				self.response.out.write(" a possible flag was: " + aproblem.flag)

				memcache.delete('problemsforteam' + userdata.teamname)
				memcache.delete('scoreboard')
					