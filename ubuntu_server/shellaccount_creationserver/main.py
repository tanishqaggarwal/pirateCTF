import webapp2
import jinja2
import json
from paste import httpserver

from securefunctions import *

import os, pwd, grp, random, subprocess

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),"static/html")),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class IndexHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(JINJA_ENVIRONMENT.get_template("index.html").render({}))

class ShellCreationHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(JINJA_ENVIRONMENT.get_template("createshell.html").render({}))
    def post(self):
        teamswaccount = open("teamswithaccounts.txt", "r")
        teamswithaccounts = teamswaccount.read().splitlines()
        teamswaccount.close()

        try:
            teamname = decrypt(self.request.get("teamname"))
        except:
            self.response.out.write("invalid team name or encryption invalid")
            return
        teamslice = teamname[0:24]
        teamname = teamname[24:]
        if teamslice == return_pass_hash_secret() and teamname not in teamswithaccounts:
            randomuser = "%0.5d" % random.randint(0,99999)
            randompassword = "%0.7d" % random.randint(0,9999999)
            shell_username = "piratenumber" + str(randomuser)
            shell_password = str(randompassword)

            madeusername = False
            while not madeusername:
                for user in pwd.getpwall():
                    if user[0] != shell_username:
                        madeusername = True
                    else:
                        madeusername = False
                        randomuser = "%0.5d" % random.randint(0,99999)
                        randompassword = "%0.7d" % random.randint(0,9999999)
                        shell_username = "piratenumber" + str(randomuser)
                        shell_password = str(randompassword)

            os.system("sudo useradd -M -G ctf2015teams -p " + shell_password + " " + shell_username)
            
            self.response.out.write(json.dumps({
                "shell_username" : shell_username,
                "shell_password" : shell_password,
                }))

            newteamswithaccounts = open("teamswithaccounts.txt","a")
            newteamswithaccounts.write(teamname + "\n")
            newteamswithaccounts.close()
        else:
            self.response.out.write("team shell account already exists (or possible encryption issue)")

app = webapp2.WSGIApplication([
    ("/",IndexHandler),
    ("/createshell",ShellCreationHandler),
], debug=True)

def main():
    httpserver.serve(app,host="localhost",port=6969)

if __name__ == '__main__':
    main()