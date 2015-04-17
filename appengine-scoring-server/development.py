from google.appengine.ext import ndb
from google.appengine.api import users
from db import *

import webapp2
import jinja2
import os
import math
import logging
from random import randint
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
            logging.info("Welcome to the PirateCTF development data generation service.")
            logging.info("Currently generating data.")
            insertion = [] 
            insertion += self.produce_sample_problems()
            insertion += self.produce_sample_teams()
            insertion += self.produce_sample_users()
            insertion += self.produce_sample_updates()
            insertion += self.produce_sample_microupdates()
            logging.info("Data generated, beginning insertion into datastore.")
            ndb.put_multi(insertion)
            logging.info("Data inserted into data store.")
            self.response.out.write(jinja_environment.get_template("testdataproduced.html").render())
        else:
            self.response.out.write(jinja_environment.get_template("not_on_dev.html").render())
    def produce_sample_problems(self):
        problemtypes = ["Forensics","Web Exploit","Binary Exploit","Reverse Engineering","Cryptography","Web Reconnaissance","Algorithms","Master Challenge"]
        logging.info("Generating problems.")
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
            theproblem.problem_type = problemtypes[(x - 1) % 7] if float(x) / float(NUMBER_PROBLEMS) < 0.8 else "Master Challenge"

            if x >= 3:
                theproblem_num_parents = randint(0,3)
            else:
                theproblem_num_parents = randint(0,x - 1)

            parent_ids = []
            for y in range(0,theproblem_num_parents):
                parentIn = False
                while not parentIn:
                    parent_id = "Problem " + str(randint(1,x))
                    if parent_id not in parent_ids:
                        parent_ids.append(parent_id)
                        parentIn = True

            theproblem.problem_parents = parent_ids

            problems.append(theproblem)

        logging.info("Problems generated.")
        return problems
    def produce_sample_users(self):
        logging.info("Generating users.")
        theusers = []
        for x in range(1,NUMBER_USERS + 1):
            theuser = users.User("pirateuser" + str(x) + "@piratectf.com")
            userobject = Users(user = theuser, username = theuser.nickname())
            userobject.teamname = "Team " + str(((x - 1) % NUMBER_TEAMS) + 1)
            userobject.classname = "Class " + str(((x - 1) % NUMBER_CLASSES) + 1)
            theusers.append(userobject)
        logging.info("Users generated.")
        return theusers
    def produce_sample_teams(self):
        logging.info("Generating teams.")
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
            theteam.points            = randint(1,1000) * 10
            theteam.passphrase        = "passphrase" + str(x)
            theteam.teamtype          = "Competitive" if x % 1000 != 0 else "Observer"
            teams.append(theteam)
        logging.info("Teams generated.")
        return teams
    def produce_sample_updates(self):
        logging.info("Generating updates.")
        updates = []
        for x in range(1,NUMBER_UPDATES + 1):
            theupdate = Updates()
            theupdate.title = "Update " + str(x)
            theupdate.update = "Text for update " + str(x)
            updates.append(theupdate)
        logging.info("Updates generated.")
        return updates
    def produce_sample_microupdates(self):
        logging.info("Generating microupdates.")
        microupdates = []
        for x in range(1,NUMBER_MICROUPDATES + 1):
            themicroupdate = MicroUpdates()
            themicroupdate.title = "Micro Update " + str(x)
            themicroupdate.update = "Text for microupdate " + str(x)
            microupdates.append(themicroupdate)
        logging.info("Microupdates generated.")
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
            self.response.out.write(jinja_environment.get_template("cookieproducer_action.html").render({
                "cookie" : thecookie,
            }))
        else:
            self.response.out.write(jinja_environment.get_template("not_on_dev.html").render())

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
                self.response.out.write(jinja_environment.get_template("cookiedecoder_action.html").render({
                        "valid" : True,
                        "cookie" : thecookie,
                    }))
            except:
                self.response.out.write(jinja_environment.get_template("cookiedecoder_action.html").render({
                        "valid" : False,
                    }))
        else:
            self.response.out.write(jinja_environment.get_template("not_on_dev.html").render())


