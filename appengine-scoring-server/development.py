from google.appengine.ext import ndb
from google.appengine.api import users
from db import *

import webapp2
import jinja2
import os
import math
import logging
from securefunctions import *

import pickle

#The numbers are large and fairly unrealistic on purpose
NUMBER_DIFFICULTIES = 7
PROBLEMS_PER_DIFFICULTY = 8
NUMBER_PROBLEMS = PROBLEMS_PER_DIFFICULTY * NUMBER_DIFFICULTIES
NUMBER_CLASSES = 20
NUMBER_TEAMS = 50 * NUMBER_CLASSES
NUMBER_USERS = 5 * NUMBER_TEAMS
NUMBER_UPDATES = 10
NUMBER_MICROUPDATES = 500

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader([os.path.join(os.path.dirname(__file__), 'html'), 
                                    os.path.join(os.path.dirname(__file__), 'html/development')]))

def graderfunction(flag,x):
    if flag == "flag_for_problem_" + str(x):
        return True
    else:
        return False

class ProduceTestData(webapp2.RequestHandler):
    def get(self):
        if "Development" in os.environ['SERVER_SOFTWARE']:
            logging.info("currently generating data")
            insertion = [] 
            insertion += self.produce_sample_problems()
            insertion += self.produce_sample_classes()
            insertion += self.produce_sample_teams()
            insertion += self.produce_sample_users()
            insertion += self.produce_sample_updates()
            insertion += self.produce_sample_microupdates()
            logging.info("data generated, beginning insertion into DB")
            ndb.put_multi(insertion)
            logging.info("data inserted into db")
            self.response.out.write("test data produced")
        else:
            self.response.out.write("not on development server")
    def produce_sample_problems(self):
        problemtypes = ["Forensics","Web Exploit","Binary Exploit","Reverse Engineering","Cryptography","Web Reconnaissance","Master Challenge","Algorithms"]
        logging.info("generating problems")
        problems = []
        for x in range(1,NUMBER_PROBLEMS + 1):
            theproblem = Problems()
            theproblem.title = "Problem " + str(x)
            theproblem.text = "Some text of problem " + str(x)
            theproblem.hint = "This is a shady hint for problem " + str(x)
            theproblem.points = int((math.floor(x / PROBLEMS_PER_DIFFICULTY) + 1.0) * 20)
            theproblem.buy_for_points = theproblem.points - 10
            theproblem.graderfunction = pickle.dumps(graderfunction(theproblem.flag,x))
            theproblem.flag = "flag_for_problem_" + str(x)
            theproblem.problem_type = problemtypes[(x - 1) % 8]
            theproblem.problem_parents = [str("Problem " + str(x - 1))] if x > 1 else []
            theproblem.problem_children = [str("Problem " + str(x + 1))] if x < NUMBER_PROBLEMS else []
            problems.append(theproblem)
        logging.info("problems generated")
        return problems
    def produce_sample_users(self):
        logging.info("generating users")
        theusers = []
        for x in range(1,NUMBER_USERS + 1):
            theuser = users.User("pirateuser" + str(x) + "@piratectf.com")
            userobject = Users(user = theuser, username = theuser.nickname())
            userobject.teamname = "Team " + str(((x - 1) % NUMBER_TEAMS) + 1)
            userobject.classname = "Class " + str(((x - 1) % NUMBER_CLASSES) + 1)
            theusers.append(userobject)
        logging.info("users generated")
        return theusers
    def produce_sample_teams(self):
        logging.info("generating teams")
        teams = []
        for x in range(1,NUMBER_TEAMS + 1):
            theteam = Teams()
            theteam.teamname          = "Team " + str(x)
            theteam.school            = "School " + str(x)
            theteam.adult_coordinator = "pirateteacher" + str(x) + "@piratectf.com"
            theteam.postal_address    = str(x) + " Pirate Way,\nThe Ship, CA 69696"
            theteam.phone             = "(609)-" + str(x)
            theteam.shell_username    = "piratectfusername" + str(x)
            theteam.shell_password    = "piratectfpassword" + str(x)
            theteam.passphrase        = "passphrase" + str(x)
            theteam.teamtype          = "Competitive" if x % 1000 != 0 else "Observer"
            teams.append(theteam)
        logging.info("teams generated")
        return teams
    def produce_sample_classes(self):
        logging.info("generating classes")
        classes = []
        for x in range(1,NUMBER_CLASSES + 1):
            theclass = Classes()
            theclass.classname = "Class " + str(x)
            theclass.classpassphrase = "passphrase" + str(x)
            theclass.classadult_firstname = "Pirate"
            theclass.classadult_lastname = "Teacher"
            theclass.classadult_email = "pirateteacher@school.edu"
            theclass.classadult_phonenumber = "(609)-" + str(x)
            theclass.classadult_postaladdress = str(x) + " Pirate Way,\nThe Ship, CA 69696"
            theclass.class_school = "School " + str(x)
            classes.append(theclass)
        logging.info("classes generated")
        return classes
    def produce_sample_updates(self):
        logging.info("generating updates")
        updates = []
        for x in range(1,NUMBER_UPDATES + 1):
            theupdate = Updates()
            theupdate.title = "Update " + str(x)
            theupdate.update = "Text for update " + str(x)
            updates.append(theupdate)
        logging.info("updates generated")
        return updates
    def produce_sample_microupdates(self):
        logging.info("generating microupdates")
        microupdates = []
        for x in range(1,NUMBER_MICROUPDATES + 1):
            themicroupdate = MicroUpdates()
            themicroupdate.title = "Micro Update " + str(x)
            themicroupdate.update = "Text for microupdate " + str(x)
            microupdates.append(themicroupdate)
        logging.info("microupdates generated")
        return microupdates

class CookieProducer(webapp2.RequestHandler):
    def get(self):
        if "Development" in os.environ["SERVER_SOFTWARE"]:
            self.response.out.write(jinja_environment.get_template("cookieproducer.html").render())
        else:
            self.response.out.write("not on development server")
    def post(self):
        if "Development" in os.environ["SERVER_SOFTWARE"]:
            data = self.request.get("userobject")
            thecookie = encrypt(data)
            self.response.out.write("The cookie: " + thecookie)
            self.response.out.write("""<br /><br /><a href = "/dev/cookieproducer"><button>Back to Cookie Producer</button></a>""")
        else:
            self.response.out.write("not on development server")

class CookieDecoder(webapp2.RequestHandler):
    def get(self):
        if "Development" in os.environ["SERVER_SOFTWARE"]:
            self.response.out.write(jinja_environment.get_template("cookiedecoder.html").render())
        else:
            self.response.out.write("not on development server")
    def post(self):
        if "Development" in os.environ["SERVER_SOFTWARE"]:
            data = self.request.get("userobject")
            try:
                thecookie = decrypt(data)
                self.response.out.write("The decrypted data: " + thecookie)
            except:
                self.response.out.write("Hey, that data you provided wasn't actually valid.")
            self.response.out.write("""<br /><br /><a href = "/dev/cookiedecoder"><button>Back to Cookie Decoder</button></a>""")
        else:
            self.response.out.write("not on development server")


