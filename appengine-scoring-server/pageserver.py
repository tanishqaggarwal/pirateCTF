#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

import webapp2
import jinja2
import os
import json
import datetime
from db import *
from securefunctions import *
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import urlfetch
import urllib2
import urllib

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'html')))

DOMAIN_NAME = "45.55.182.189"
SHELL_CREATION_PORT = str(6969)
SHELL_SERVER_PORT = str(22)

def timeformat(datetime):
    datetimestring = datetime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    return datetimestring[:len(datetimestring) - 2] + ":" + datetimestring[len(datetimestring) - 2:]

class Index(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("index.html")
        template_values = {}
        self.response.out.write(template.render(template_values))

class DisplayUpdates(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("updates.html")
        template_values = self.populateServerContent()
        self.response.out.write(template.render(template_values))
    def populateServerContent(self):
        data = memcache.get('updates')
        microdata = memcache.get('microupdates')
        if not data:
            updateslist = []
            updates_list = ndb.gql("SELECT * FROM Updates ORDER BY time DESC").fetch(limit=None)
            
            for update in updates_list:
                updatedata = {
                    "title"  : update.title,
                    "update" : update.update,
                    "time"   : update.time.strftime("%b %d %Y %H:%M"),
                }
                updateslist.append(updatedata)

            memcache.add('updates',updateslist)

        if not microdata:
            microupdateslist = []
            microupdates_list = ndb.gql("SELECT * FROM MicroUpdates ORDER BY time DESC").fetch(limit=None)

            for microupdate in microupdates_list:
                microupdatedata = {
                    "title"  : microupdate.title,
                    "update" : microupdate.update,
                    "time"   : microupdate.time.strftime("%b %d %Y %H:%M"),
                }
                microupdateslist.append(microupdatedata)

            memcache.add('microupdates',microupdateslist)
        
        return {"microupdates" : memcache.get("microupdates"), "updates" : memcache.get("updates")}

class DisplayProblems(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                template = jinja_environment.get_template("problems.html")
                template_values = self.populateServerContent(userobject)
                self.response.out.write(template.render(template_values))
            else:
                self.response.set_cookie("redirectto","/problems")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/problems")
            self.redirect("/login")

    def populateServerContent(self,userdata):
        data = memcache.get('problemsforteam' + userdata['teamname'])
        if not data:
            problemquery = ndb.gql("SELECT * FROM Problems ORDER BY points ASC, title ASC").fetch(limit=1000)
            teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn",teamn = userdata['teamname']).get()
            solved_problems = []
            for solved_problem in teamquery.successful_attempts:
                solved_problems.append({
                    "title"   : solved_problem["problem"],
                    "buyed"   : solved_problem["buyed"],
                    "user"    : solved_problem["user"],
                    "flag"    : solved_problem["attempt"],
                    })

            problems = []
            for problem in problemquery:
                problemdata = {
                    "hash"            : hash_pass(problem.title),
                    "title"           : problem.title,
                    "category"        : problem.problem_type,
                    "num_solved"      : problem.number_solved,
                    "points"          : problem.points,
                    "buy_for_points"  : problem.buy_for_points,
                    "text"            : problem.text,
                    "hint"            : problem.hint,
                    "problem_parents" : problem.problem_parents,
                    "problem_children": problem.problem_children,
                    "solved"          : False,
                    "buyed"           : False,
                }
                if self.app.config.get("problem_hierarchy"):
                    problemdata["problem_parents"] = problem.problem_parents
                    problemdata["problem_children"] = problem.problem_children
                for problemsolved in solved_problems: #A for loop inside a for loop is inefficient, but it gets the job done and doesn't take too much time since the number of problems is small
                    if problemsolved.title == problemdata.title:
                        problemdata.append("user",problemsolved.user)
                        problemdata.buyed = problemsolved.buyed
                        problemdata.solved = True
                        problemdata.flag = problemsolved.flag
                problems.append(problemdata)

            data = {
                "allproblems" : problems,
            }
            memcache.add('problemsforteam' + userdata['teamname'],data)
            return data
        else:
            return data

class About(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("about.html")
        template_values = {}
        self.response.out.write(template.render(template_values))

class Shell(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                template = jinja_environment.get_template("shell.html")
                template_values = self.populateServerContent(userobject)
                self.response.out.write(template.render(template_values))
            else:
                self.response.set_cookie("redirectto","/shell")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/shell")
            self.redirect("/login")
    def populateServerContent(self,userdata):
        data = memcache.get('shellfor' + userdata['teamname'])
        if not data:
            data = {}
            teamquery = ndb.gql("SELECT shell_username, shell_password FROM Teams WHERE teamname = :teamn",teamn=userdata['teamname']).get()
            data['shell_username'] = teamquery.shell_username
            data['shell_password'] = teamquery.shell_password
            memcache.add('shellfor' + userdata['teamname'],data)
        data["IP"] = DOMAIN_NAME
        data["PORT"] = SHELL_SERVER_PORT
        return data

class Chat(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                template = jinja_environment.get_template("chat.html")
                self.response.out.write(template.render({}))
            else:
                self.response.set_cookie("redirectto","/chat")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/chat")
            self.redirect("/login")

class Scoreboard(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("scoreboard.html")
        template_values = self.populateServerContent()
        self.response.out.write(template.render(template_values))
    def populateServerContent(self):
        data = memcache.get('scoreboard')
        if not data:
            teamquery  = ndb.gql("SELECT * FROM Teams ORDER BY points DESC").fetch(limit=None)
            data = {
                "data" : []
            }
            teamdata = []
            for team in teamquery:
                teamdat = memcache.get("teaminfoforteam" + team.teamname)
                if teamdat:
                    data["data"].append(teamdat)
                else:
                    teamdat = {
                        "teamname" : team.teamname, 
                        "teamtype" : team.teamtype,
                        "school" : team.school,
                        "points" : team.points,
                        "time" : "",
                    }
                    highesttime = datetime.datetime(1900,1,1,0,0,0,0)
                    for attempts in team.successful_attempts:
                        if highesttime < attempts.time:
                            highesttime = attempts.time
                    teamdat["time"] = timeformat(highesttime)
                    memcache.add("teaminfoforteam" + team.teamname,teamdat)
                    data["data"].append(teamdat)
            memcache.add('scoreboard',data)
        return data
        
class ShowProblemsSolved(webapp2.RequestHandler):
    def post(self):
        senddata = memcache.get("showproblemsforteam" + self.request.get("teamname"))
        if senddata:
            self.response.out.write(senddata)
        else:
            data = memcache.get("problemsforteam" + self.request.get("teamname"))
            if not data:
                problemquery = ndb.gql("SELECT * FROM Problems").fetch(limit=None)
                teamquery = ndb.gql("SELECT successful_attempts FROM Teams WHERE teamname = :teamn",teamn = userdata['teamname']).get()
                solved_problems = []
                for solved_problem in teamquery.successful_attempts:
                    solved_problems.append({
                        "title"   : solved_problem["problem"],
                        "buyed"   : solved_problem["buyed"],
                        "user"    : solved_problem["user"],
                        "flag"    : solved_problem["attempt"],
                        "time"    : timeformat(solved_problem["time"]),
                        })

                problems = []
                for problem in problemquery:
                    problemdata = {
                        "title"           : problem["title"],
                        "category"        : problem["category"],
                        "num_solved"      : problem["num_solved"],
                        "points"          : problem["points"],
                        "buy_for_points"  : problem["buy_for_points"],
                        "text"            : problem["problem"],
                        "hint"            : problem["hint"],
                        "problem_parents" : problem["problem_parents"],
                        "problem_children": problem["problem_children"],
                        "solved"          : False,
                        "buyed"           : False,
                        "time"            : "",
                    }
                    for problemsolved in solved_problems: #A for loop inside a for loop is inefficient, but it gets the job done and doesn't take too much time since the number of problems is small
                        if problemsolved.title == problemdata.title:
                            problemdata.append("user",problemsolved.user)
                            problemdata.buyed = problemsolved.buyed
                            problemdata.solved = True
                            problemdata.flag = problemsolved.flag
                            problemdata.time = problemsolved.time
                    problems.append(problemdata)

                data = {
                    "allproblems" : problems,
                }
                memcache.add('problemsforteam' + userdata['teamname'],data)
                self.response.out.write(json.dumps(data))

            senddata = []
            for problem in data.allproblems:
                problem.pop(user,None)
                problem.pop(flag,None)
                problem.pop(text)
                problem.pop(hint)
                problem.pop(num_solved)
                problem.pop(category)
                senddata.append(problem)

            self.response.out.write(json.dumps(senddata))
            memcache.add("showproblemsforteam" + self.request.get("teamname"),json.dumps(senddata))

class Class(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                template_values = self.populateServerContent(userobject)
                if template_values['authorized'] == "authorized":
                    template_authorized = jinja_environment.get_template("class_authorized.html")
                    self.response.out.write(template_authorized.render(template_values))
                elif template_values['authorized'] == "notauthorized":
                    template_unauthorized = jinja_environment.get_template("class_notauthorized.html")
                    self.response.out.write(template_unauthorized.render({}))
            else:
                self.response.set_cookie("redirectto","/class")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/class")
            self.redirect("/login")
    def populateServerContent(self,userdata):
        #Show class teams, class scoreboard, class name
        if userdata['classname'] == "defaultclass":
            return { "authorized" : "notauthorized" }#aint nobody gonna spend the computing hours to calculate the scoreboard again
        data = memcache.get('classfor' + userdata['classname'])
        if not data:
            classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn",classn=userdata['classname']).get()
            teamquery  = ndb.gql("SELECT * FROM Teams WHERE classname = :classn", classn=userdata['classname']).fetch(limit=None)
            for aclass in classquery:
                data = {
                    "authorized" : "authorized",
                    "classdata" : {
                        "classname"                : userdata['classname'],
                        "classpassphrase"          : aclass.classpassphrase,
                        "classadult_email"         : str(aclass.classadult_email),
                        "classadult_name"          : aclass.classadult_firstname + aclass.classadult_lastname,
                        "classadult_phonenumber"   : str(aclass.classadult_phonenumber),
                        "classadult_postaladdress" : str(aclass.classadult_postaladdress),
                        "class_school"             : aclass.class_school, 
                    },  
                    "teamdata" : []
                }
                for team in teamquery:
                    teamdat = memcache.get("teaminfoforteam" + team.teamname)
                    if teamdat:
                        data.teamdata.append(teamdat)
                    else:
                        teamdat = {
                            "teamname" : team.teamname,
                            "points" : team.points,
                            "time" : "",
                        }
                        highesttime = datetime.datetime(1900,1,1,0,0,0,0)
                        for attempt in team.successful_attempts:
                            if highesttime < attempt.time:
                                highesttime = attempt.time
                        teamdat.time = timeformat(highesttime)
                        memcache.add("teaminfoforteam" + team.teamname,teamdat)
                        data.teamdata.append(teamdat)
                memcache.add('classfor' + userdata['classname'],data)
                return data
        else:
            return data

    def post(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                typeofaction = self.request.get("typeofaction")

                if typeofaction == "changepassphrase":
                    #on the form page, indicate that any changes to the passphrase will not remove a team automatically
                    form_dictionary = {
                        "classname" : self.request.get("classname"),
                        "oldpassphrase" : self.request.get("oldpassphrase"),
                        "newpassphrase" : self.request.get("newpassphrase"),
                    }
                    classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn AND classpassphrase = :passphr",classn = form_dictionary['classname'], passphr= form_dictionary['oldpassphrase']).get()
                    if classquery:
                        for aclass in classquery:
                            aclass.classpassphrase = newpassphrase
                        self.response.out.write("passphrase changed")
                    else:
                        self.response.out.write("no class found")

                elif typeofaction == "changeclassname":
                    #on the form page, indicate that any changes to the classname will not remove any team or user
                    form_dictionary = {
                        "oldclassname" : self.request.get("oldclassname"),
                        "passphrase" : self.request.get("passphrase"),
                        "newclassname" : self.request.get("newclassname"),
                    }
                    classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn AND classpassphrase = :passphr",classn = form_dictionary['oldclassname'], passphr= form_dictionary['passphrase']).get()
                    if classquery:
                        for aclass in classquery:
                            aclass.classname = newclassname
                        teamquery = ndb.gql("SELECT * FROM Teams WHERE classname = :classn", classn = form_dictionary['oldclassname']).fetch(limit=None)
                        for team in teamquery:
                            team.classname = newclassname
                            team.put()
                        userquery = ndb.gql("SELECT * FROM Users WHERE classname = :classn", classn = form_dictionary['classname']).fetch(limit=None)
                        for auser in userquery:
                            auser.classname = form_dictionary['newclassname']
                            auser.put()
                        if userobject.classname == form_dictionary['classname']:
                            userobject = {
                                "username" : userobject.username,
                                "teamname" : userobject.teamname,
                                "classname" : form_dictionary['newclassname'],
                            }
                            self.response.delete_cookie("userobject")
                            self.set_cookie("userobject",encrypt(json.dumps(userobject)))
                        self.response.out.write("classname changed")
                    else:
                        self.response.out.write("no class found")

                elif typeofaction == "removeteam":
                    form_dictionary = {
                        "classname" : self.request.get("classname"),
                        "passphrase" : self.request.get("passphrase"),
                        "teamtoremove" : self.request.get("teamname"),
                    }
                    classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn AND classpassphrase = :passphr",classn = form_dictionary['classname'], passphr= form_dictionary['passphrase']).get()
                    if classquery:
                        teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn", teamn = form_dictionary['teamtoremove']).get()
                        if teamquery:
                            teamquery.classname = "defaultclass"
                            teamquery.put()
                            userquery = ndb.gql("SELECT * FROM Users WHERE teamname = :teamn", teamn = form_dictionary['teamname']).fetch(limit=None)
                            for auser in userquery:
                                auser.classname = "defaultclass"
                                auser.put()
                            if userobject.teamname == form_dictionary['teamtoremove']:
                                userobject = {
                                    "username" : userobject.username,
                                    "teamname" : userobject.teamname,
                                    "classname" : "defaultclass",
                                }
                                self.response.delete_cookie("userobject")
                                self.set_cookie("userobject",encrypt(json.dumps(userobject)))
                            self.response.out.write("team removed")
                        else:
                            self.response.out.write("no team found")
                    else:
                        self.response.out.write("no class found")
                    memcache.delete("classfor" + form_dictionary['classname'])

                elif typeofaction == "deleteclass":
                    form_dictionary = {
                        "classname" : self.request.get("classname"),
                        "passphrase" : self.request.get("passphrase"),
                    }
                    classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn AND classpassphrase = :passphr",classn = form_dictionary['classname'], passphr= form_dictionary['passphrase']).get()
                    if classquery:
                        teamquery = ndb.gql("SELECT * FROM Teams WHERE classname = :classn", teamn = form_dictionary['classname']).fetch(limit=None)
                        if teamquery:
                            for team in teamquery:
                                team.classname = "defaultclass"
                                userquery = ndb.gql("SELECT * FROM Users WHERE teamname = :teamn", teamn = team.teamname).fetch(limit=None)
                                for auser in userquery:
                                    auser.classname = "defaultclass"
                                    auser.put()
                                if userobject.teamname == team.teamname:
                                    userobject = {
                                        "username" : userobject.username,
                                        "teamname" : userobject.teamname,
                                        "classname" : "defaultclass",
                                    }
                                    self.response.delete_cookie("userobject")
                                    self.set_cookie("userobject",encrypt(json.dumps(userobject)))
                        self.response.out.write("class removed")
                        memcache.delete("classfor" + form_dictionary['classname'])

                    else:
                        self.response.out.write("no class found")

                else:
                    self.response.out.write("illegal action")
            else:
                self.response.set_cookie("redirectto","/class")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/class")
            self.redirect("/login")

class Team(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                template = jinja_environment.get_template("team.html")
                template_values = self.populateServerContent(userobject)
                self.response.out.write(template.render(template_values))
            else:
                self.response.set_cookie("redirectto","/team")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/team")
            self.redirect("/login")
    def populateServerContent(self,userdata):
        #Show user names, team score progression, team name
        data = memcache.get('teamfor' + userdata['teamname'])
        if not data:
            data = {
                "teamname" : userdata['teamname'],
                "teampassphrase" : "",
                "usernames" : [],
                "points" : 0
            }
            userquery = ndb.gql("SELECT username FROM Users WHERE teamname = :teamn", teamn = userdata['teamname']).fetch(limit=None)
            teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn", teamn = userdata['teamname']).get()
            data['teampassphrase'] = teamquery.passphrase
            for users in userquery:
                data['usernames'].append(users.username)
            data['points'] = teamquery.points
            memcache.add('teamfor' + userdata['teamname'],data)
            return data
        else:
            return data
    def post(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                typeofaction = self.request.get("typeofaction")
                if typeofaction == "changepassphrase":
                    form_dictionary = {
                        "teamname" : self.request.get("teamname"),
                        "oldteampassphrase" : self.request.get("oldteampassphrase"),
                        "newteampassphrase" : self.request.get("newteampassphrase")
                    }
                    teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND passphrase = :passphr",teamn=form_dictionary['teamname'],passphr=form_dictionary['oldteampassphrase']).get()
                    if teamquery:
                        teamquery.passphrase = form_dictionary['newteampassphrase']
                        teamquery.put()
                        self.response.out.write("team passphrase updated")
                    else:
                        self.response.out.write("no team found")
                elif typeofaction == "changeteamname":
                    form_dictionary = {
                        "oldteamname" : self.request.get("oldteamname"),
                        "passphrase" : self.request.get("passphrase"),
                        "newteamname" : self.request.get("newteamname"),
                    }
                    teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND teampassphrase = :passphr",teamn = form_dictionary['oldteamname'], passphr= form_dictionary['passphrase']).get()
                    if teamquery:
                        teamquery.teamname = newteamname
                        teamquery.put()
                        userquery = ndb.gql("SELECT * FROM Users WHERE teamname = :teamn", teamn = form_dictionary['oldteamname']).fetch(limit=None)
                        for auser in userquery:
                            auser.teamname = newteamname
                            auser.put()
                        if userobject.teamname == form_dictionary['oldteamname']:
                            userobject = {
                                "username" : userobject.username,
                                "teamname" : form_dictionary['newteamname'],
                                "classname" : userobject.classname,
                            }
                            self.response.delete_cookie("userobject")
                            self.set_cookie("userobject",encrypt(json.dumps(userobject)))
                        self.response.out.write("teamname changed")
                    else:
                        self.response.out.write("no team found")
                elif typeofaction == "removeteamuser":
                    form_dictionary = {
                        "teamname" : self.request.get("teamname"),
                        "passphrase" : self.request.get("passphrase"),
                        "username" : self.request.get("username"),
                    }
                    teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND teampassphrase = :passphr",teamn = form_dictionary['teamname'], passphr= form_dictionary['passphrase']).get()
                    if teamquery:
                        userquery = ndb.gql("SELECT * FROM Users WHERE username = :usrn", usrn = form_dictionary['username']).get()
                        for auser in userquery:
                            auser.key.delete()
                        if json.loads(decrypt(self.request.cookies.get("userobject"))).teamname == form_dictionary['teamname']:
                            self.response.delete_cookie("userobject")
                        self.response.out.write("user removed from team")
                    else:
                        self.response.out.write("no team found")
                elif typeofaction == "deleteteam":
                    teamname = self.request.get("teamname")
                    passphrase = self.request.get("passphrase")
                    teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND teampassphrase = :passphr",teamn = form_dictionary['teamname'], passphr= form_dictionary['passphrase']).get()
                    if teamquery:
                        userquery = ndb.gql("SELECT * FROM Users WHERE teamname = :teamn", teamn = teamname).fetch(limit=None)
                        for auser in userquery:
                            auser.key.delete()
                        if json.loads(decrypt(self.request.cookies.get("userobject"))).teamname == teamname:
                            self.response.delete_cookie("userobject")
                        for attempts in teamquery.successful_attempts:
                            problemquery = ndb.gql("SELECT num_solved FROM Problems WHERE title = :titl",titl = attempts.problem).get()
                            if problemquery:
                                problemquery["num_solved"] -= 1
                                problemquery.put()

                        teamquery.key.delete()
                        self.response.out.write("team deleted")
                    else:
                        self.response.out.write("no team found")
                else:
                    self.response.out.write("illegal action")
            else:
                self.response.set_cookie("redirectto","/team")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/team")
            self.redirect("/login")


class Account(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                template = jinja_environment.get_template("account.html")
                self.response.out.write(template.render({}))
            else:
                self.response.set_cookie("redirectto","/account")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/account")
            self.redirect("/login")
    def post(self):
        if users.get_current_user():
            try:
                userobject = json.loads(decrypt(self.request.cookies.get("userobject")))
            except ValueError as e:
                self.response.out.write("invalid user cookie")
                return
            if userobject:
                typeofaction  = self.request.get("typeofaction")
                oldteam       = self.request.get("oldteam")
                oldpassphrase = self.request.get("oldpassphrase")
                newteam       = self.request.get("newteam")
                newpassphrase = self.request.get("newpassphrase")

                if typeofaction == "change team":
                    oldteamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND passphrase = :teamp",teamn=oldteam,teamp=hash_pass(oldpassphrase)).get()
                    newteamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND passphrase = :teamp",teamn=newteam,teamp=hash_pass(newpassphrase)).get()
                    if not oldteamquery:
                        self.response.out.write("old team not found")
                        return
                    elif not newteamquery:
                        self.response.out.write("new team not found")
                        return
                    else:
                        numusers = ndb.gql("SELECT * FROM Users WHERE teamname = :teamn", teamn=newteamquery.teamname).fetch(limit=None)
                        if len(numusers) >= 5:
                            self.response.out.write("new team already has five people")
                            return
                        else:
                            userquery = ndb.gql("SELECT * FROM Users WHERE username = :usrn", usrn = userobject['username']).get()
                            if userquery:
                                userobject['teamname'] = newteamquery.teamname
                                self.set_cookie("userobject",encrypt(json.dumps(userobject)))
                                self.response.out.write("success")
                            else:
                                self.response.delete_cookie("userobject")
                                self.response.out.write("invalid user cookie")
                                self.redirect("/")
                else:
                    self.response.out.write("illegal action")
                #if necessary add new action types later
            else:
                self.response.set_cookie("redirectto","/account")
                self.redirect("/login")
        else:
            self.response.set_cookie("redirectto","/account")
            self.redirect("/login")

class Login(webapp2.RequestHandler):
    #TODO: On the login page MAKE SURE there's a notice indicating you have to have cookies enabled!
    def get(self):
        if users.get_current_user():
            if self.request.cookies.get("userobject"):
                self.redirect("/problems")
            else:
                userquery = ndb.gql("SELECT * FROM Users WHERE username = :usrn", usrn = users.get_current_user().nickname()).get()
                username  = ""
                teamname  = ""
                classname = ""
                if userquery:
                    userExists = True
                    username = userquery.username
                    teamname = userquery.teamname
                    teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn", teamn = teamname).get()
                    if teamquery:
                        classname = teamquery.classname
                    else:
                        self.response.out.write("user's team not found")
                    self.response.set_cookie("userobject",encrypt(json.dumps({"username" : username, "teamname" : teamname, "classname" : classname})))
                    redirectspace = self.request.cookies.get("redirectto")
                    if not redirectspace:
                        redirectspace = "/problems"
                    self.response.delete_cookie("redirectto")
                    self.redirect(redirectspace)
                else:
                    template = jinja_environment.get_template("login.html") #page to collect user's teamname information
                    self.response.out.write(template.render({}))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        if users.get_current_user():
            teamname = self.request.get("teamname")
            passphrase = self.request.get("passphrase")
            teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn AND passphrase = :passp",teamn=teamname,passp=passphrase).get()
            if teamquery:
                newuser = Users()
                newuser.user = users.get_current_user()
                newuser.teamname = teamquery.teamname
                newuser.username = users.get_current_user().nickname()
                newuser.classname = teamquery.classname
                self.response.set_cookie("userobject",encrypt(json.dumps({"username" : newuser.username, "teamname" : newuser.teamname, "classname" : newuser.classname})))
                newuser.put()
                self.response.out.write("user logged in")
            else:
                self.response.out.write("team not found or passphrase incorrect")
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Logout(webapp2.RequestHandler):
    def get(self):
        if self.request.cookies.get("userobject"):
            self.response.delete_cookie("userobject")
        self.redirect(users.create_logout_url("/"))

class Register(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("register.html")
        self.response.out.write(template.render({}))
    def post(self):
        #team information from post request
        registrationmode = self.request.get("registrationmode")

        if registrationmode == "team":

            form_dictionary = {
                "teamname" : self.request.get("teamname"),
                "school" : self.request.get("school"),
                "passphrase" : self.request.get("passphrase"),
                "adult_coordinator" : self.request.get("adult_coordinator"),
                "address_line1" : self.request.get("address_line1"),
                "address_line2" : self.request.get("address_line2"),
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
            if form_dictionary['teamname'] != "defaultteam":
                teamquery = ndb.gql("SELECT * FROM Teams WHERE teamname = :teamn OR passphrase = :passphr",teamn=form_dictionary['teamname'], passphr=form_dictionary['passphrase']).fetch(limit=None)
                exists = False
                for team in teamquery:
                    exists = True
            else:
                exists = True

            if not exists:
                teamobject = Teams()
                
                for formfield, formvalue in form_dictionary.items():
                    setattr(teamobject,formfield,formvalue)

                self.response.out.write("submitting shell account creation request")
                try:
                    shellinfo = json.loads(urlfetch.fetch("https://" + DOMAIN_NAME + ":" + SHELL_CREATION_PORT + "/createshell", payload = urllib.encode({
                        "teamname" : encrypt(return_pass_hash_secret() + teamname),
                        }), method = "POST").content)
                except:
                    self.response.out.write("error in shell account creation")
                    return
                teamobject.shell_username = shellinfo.shell_username
                teamobject.shell_password = shellinfo.shell_password
                teamobject.put()

                teamupdate = MicroUpdates()
                teamupdate.title = "New Team Added: " + form_dictionary['teamname']
                teamupdate.update = "Team \"" + form_dictionary['teamname'] + "\" of " + form_dictionary['school'] + "has joined pirateCTF!"
                teamupdate.put()

                self.response.out.write("team created")
                return
            else:
                self.response.out.write("team name or passphrase already taken")
                return

        elif registrationmode == "class":
            formdictionary = {
                "classname" : self.request.get("classname"),
                "classadult_school" : self.request.get("classadult_school"),
                "classpassphrase" : self.request.get("classpassphrase"),
                "classadult_email" : self.request.get("classadult_email"),
                "classadult_addressline1" : self.request.get("classadult_addressline1"),
                "classadult_addressline2" : self.request.get("classadult_addressline2"),
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

            #check if team doesn't already exist
            classquery = ndb.gql("SELECT * FROM Classes WHERE classname = :classn OR classpassphrase = :classpassphr",classn=classname, classpassphr=classpassphrase).fetch(limit=None)
            exists = False
            for anyclass in classquery:
                exists = True
            if not exists:
                newclass = Classes()
                
                for formfield, formvalue in form_dictionary.items():
                    setattr(newclass,formfield,formvalue)

                newclass.put()  
                self.response.out.write("class created")
            else:
                self.response.out.write("class name or passphrase already taken")