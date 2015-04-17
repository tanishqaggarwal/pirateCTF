#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

#Admin console backend logic.
#Frontend and JS Files.
# -- First up, problemsort.js since that seems to be fun.

import webapp2
from grader import *
from pageserver import *
from adminconsole import *
from development import *
from securefunctions import *

config = {
    "problem_hierarchy" : True, #use a problem hierarchical structure or just plain old CTF-style? TODO: implement in problems.html
    "problem_explanation" : True, #require submission of a problem explanation or not? TODO: implement in problems.html
    "buyable" : True, #Can users buy problems? TODO: implement in problems.html
    "competition_starts" : datetime.datetime(2015,1,1,12,0,0,0), #When competition starts TODO: implement (front and back)
    "competition_ends" : datetime.datetime(2015,12,1,12,0,0,0) #When competition ends TODO: implement (front and back)
    "permit_viewing" : True, #allow other users to see what problems a team has solved from the scoreboard TODO: implement (front and back)
}


application = webapp2.WSGIApplication(routes=[
    #Serves pages to main users - pageserver.py
    ('/', Index),
    ('/index', Index),
    ('/about', About),
    ('/login',Login),
    ('/logout',Logout),
    ('/register', Register),
    ('/scoreboard',Scoreboard),
    ('/showteamproblems',ShowProblemsSolved),
    ('/problems',DisplayProblems),
    ('/shell',Shell),
    ('/chat',Chat),
    ('/team',Team),
    ('/updates',DisplayUpdates),
] + [
    #Grader - grader.py
    ('/grader',Grader),
    ('/buyer',Buyer),
] + [
    #The administration console - adminconsole.py. IS BEING ACTIVELY DEVELOPED, WILL NOT BE INCLUDED AS OF NOW.
    #('/admin/index',AdminConsole),
    #('/admin/actions/addproblem',AdminConsoleAddProblem),
    #('/admin/adminrequest/teammembers',AdminConsoleInformationRequestTeamMembers),
    #('/admin/pages/addproblem',AdminConsoleAddProblem),
] + [
    #Functions for encryption and hashing - securefunctions.py
    ('/security/cookiechecker',CookieChecker),
] + [
    #For temporary, development use only - development.py
    ('/dev/producetestdata',ProduceTestData),
    ('/dev/cookieproducer',CookieProducer),
    ('/dev/cookiedecoder',CookieDecoder),
], debug=True, config = config)