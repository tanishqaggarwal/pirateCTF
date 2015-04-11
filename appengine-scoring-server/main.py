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
    "problem_hierarchy" : True,
    "problem_explanation" : True,
    "buyable" : True,
} #set of parameters that enables various pirateCTF-specific features, such as the ability to have a problem hierarchy, the requirement for users to submit an explanation for every problem attempt, and the ability for users to buy flags for points.

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