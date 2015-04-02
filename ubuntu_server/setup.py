#Sets up shell server with the account creation HTTP server, as well as shellinabox. Sets up the problems with the appropriate permissions.

import os
from shellaccount_creationserver.securefunctions import *

#get project files and unzip them here
#os.system("wget http://github.com/tanishqaggarwal/shell-ctf-platform.zip")
#os.system("tar -xzvf + " + os.path.join(os.path.dirname(__file__),"shell-ctf-platform.zip")) #check syntax

#install webapp2 dependencies
os.system("sudo apt-get install -y python-pip") #find option to automatically say "Y" at the install prompt
os.system("sudo apt-get --upgrade pip")
os.system("sudo pip install WebOb")
os.system("sudo pip install paste")
os.system("sudo pip install webapp2")
os.system("sudo pip install pycrypto")
os.system("sudo pip install jinja2")

#start servers
os.system("python " + os.path.join(os.path.dirname(__file__),"shellaccount_creationserver/main.py")) #starts webapp2 shell account creation server

#Configure message of the day
os.system("sudo cp " + os.path.join(os.path.dirname(__file__),"miscellaneous_files/motd") + " /etc/motd")
os.system("sudo update-motd")

#install shellinabox and configure it
os.system("sudo apt-get install -y shellinabox")
#configure shellinabox, if necessary

#set up some things for user accounts
os.system("sudo groupadd pirates")
os.system("sudo useradd -G pirates masterpirate -p " + encrypt("masterpiratepassword")) #might need this, don't need it right now. I just added it just for fun.

#copy problems from shell_problems folder to the /home directory
os.system("sudo cp -r " + os.path.join(os.path.dirname(__file__),"shell_problems") + " /home/") #check os path syntax

#create problemsu group, create user in problemsu for each binary exploit problem
os.system("sudo addgroup problemsu")
#for folder in shell_problems:
#get folder name, create user and add him to the group 
os.system("sudo useradd -G problemsu probsu_problemname")

#on a random note, its insane how much the "os" module can do. It literally set up the entire system for me!