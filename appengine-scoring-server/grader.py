#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

from db import *
from securefunctions import *
import json
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import users
import datetime
import webapp2

import pickle

def delete_memcache_keys(userobject,problem,problemchildren):
    memcache.delete('problemsforteam' + userobject["teamname"])
    memcache.delete("problem" + problem + "forteam" + userobject["teamname"])
    for children in problemchildren:
        memcache.delete("problem" + children + "forteam" + userobject["teamname"])
    memcache.delete('showproblemsforteam' + userobject["teamname"])
    memcache.delete('scoreboard')
    memcache.delete('accountfor' + userobject["teamname"])
    memcache.delete("teaminfoforteam" + userobject["teamname"])

class Grader(webapp2.RequestHandler):
    def post(self):
        problem = self.request.get("problemidentifier")
        attempt = self.request.get("attempt")
        explanation = self.request.get("explanation")
        ipaddr  = self.request.remote_addr

        userobject = ""
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return

        teamselect = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = userobject["teamname"]).get()
        problemattempts = []
        successfulproblemattempts = []
        if not teamselect:
            self.response.out.write("invalid user object")
            return

        aproblem = ndb.gql("SELECT * FROM Problems WHERE title = :titl",titl=problem).get()
        if not aproblem:
            self.response.out.write("not a valid problem identifier")
            return

        if not explanation and self.app.config.get("problem_explanation"):
            self.response.out.write("explanation required for flag submission")
            return
        else:
            problemdata = memcache.get(aproblem.title)
            if not problemdata:
                memcache.add(aproblem.title,aproblem)
                problemdata = memcache.get(aproblem.title)
            func = pickle.loads(aproblem.graderfunction)

            functionValidated = False
            try:
                functionValidated = func(attempt)
            except:
                functionValidated = False

            flagcorrect = functionValidated or (attempt == aproblem.flag)
            if flagcorrect:
                problemattempts = teamselect.problems_attempted
                successfulproblemattempts = teamselect.successful_attempts

                solved_parent = False
                for anyproblem in successfulproblemattempts:
                    if anyproblem.problem in aproblem.problem_parents:
                        solved_parent = True
                    if anyproblem.problem == problem:
                        self.response.out.write("already solved")
                        return

                if not aproblem.problem_parents:
                    solved_parent = True

                if not solved_parent and self.app.config.get("problem_hierarchy"):
                    self.response.out.write("at least one parent problem not solved/bought")
                    return
                    
                aproblem.number_solved += 1
                aproblem.put()                                  
                theproblem             = ProblemAttempts()
                theproblem.attempt     = attempt
                theproblem.successful  = True
                theproblem.problem     = problem
                theproblem.explanation = explanation
                theproblem.ip          = ipaddr
                theproblem.user        = userobject['username']
                problemattempts.append(theproblem)
                successfulproblemattempts.append(theproblem)

                teamselect.problems_attempted = problemattempts
                teamselect.points            += aproblem.points
                teamselect.put()
                self.response.out.write("solved")

                delete_memcache_keys(userobject, problem, aproblem.problem_children)                
            else:
                problemattempts = teamselect.problems_attempted
                for anyproblem in problemattempts:
                    if anyproblem.problem == problem and anyproblem.attempt == attempt:
                        self.response.out.write("already tried this")
                        return
                
                theproblem             = ProblemAttempts()
                theproblem.attempt     = attempt
                theproblem.successful  = False
                theproblem.problem     = problem
                theproblem.explanation = explanation
                theproblem.ip          = ipaddr
                theproblem.user        = userobject['username']
                problemattempts.append(theproblem)

                teamselect.problems_attempted = problemattempts
                teamselect.put()
                self.response.out.write("incorrect")

class Buyer(webapp2.RequestHandler):
    def post(self):
        if not self.app.config["buyable"]:
            self.response.out.write("buying problems is not enabled")
            return

        problem = self.request.get("problemidentifier")
        ipaddr  = self.request.remote_addr

        userobject = ""
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return

        teamselect = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = userobject["teamname"]).get()
        if not teamselect:
            self.response.out.write("invalid user object")
            return

        aproblem = ndb.gql("SELECT * FROM Problems WHERE title = :titl",titl=problem).get()
        if not aproblem:
            self.response.out.write("not a valid problem identifier")
            return
        else:
            solved_parent = False
            for anattempt in teamselect.successful_attempts:
                if anattempt.problem in aproblem.problem_parents:
                    solved_parent = True
                if anattempt.problem == problem:
                    self.response.out.write("already bought/solved")
                    return

            if not aproblem.problem_parents:
                    solved_parent = True

            if not solved_parent:
                self.response.out.write("at least parent problem not solved/bought")
                return

            if aproblem.buy_for_points > teamselect.points:
                self.response.out.write("not enough points")
                return

            theproblem             = ProblemAttempts()
            theproblem.attempt     = aproblem.flag
            theproblem.successful  = True
            theproblem.problem     = problem
            theproblem.explanation = "bought"
            theproblem.ip          = ipaddr
            theproblem.buyed       = True

            teamselect.problems_attempted.append(theproblem)
            teamselect.successful_attempts.append(theproblem)

            teamselect.points -= aproblem.buy_for_points
            teamselect.points += aproblem.points
            teamselect.put()
            self.response.out.write(aproblem.flag)

            delete_memcache_keys(userobject,problem,aproblem.problem_children)
                    