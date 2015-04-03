#Sets up shell server with the account creation HTTP server, as well as shellinabox. Sets up the problems with the appropriate permissions.
#IMPORTANT: check os path syntax.

import os
from shellaccount_creationserver.securefunctions import *

#lock down machine from root access, create admin user instead with root privileges
os.system("sudo useradd -G sudo -p " + return_admin_password() + " admin")
os.system("sudo passwd -dl root")

#set up public ssh key and github authorization to download repo
os.system("ssh-keygen -t rsa -f /home/admin/.ssh/id_rsa -N \"\" ")
publickey = open("/home/admin/.ssh/id_rsa.pub").read()

#programmatically connect to github and add ssh key to github
os.system("curl -H \"Authorization: token " + return_github_oauth_token() + "\" https://api.github.com") 
os.system("curl -u \" " + return_github_username() + "\" --data '{\"title\":\"piratectf-authentication\",\"key\":\"" + publickey + "\"}' https://api.github.com/user/keys")

#get project files and unzip them here
os.system("git clone https://github.com/tanishqaggarwal/pirateCTF.git /home/piratectfrepository")

#install webapp2 dependencies
os.system("sudo apt-get install -y python-pip")
os.system("sudo apt-get --upgrade pip")
os.system("sudo pip install WebOb")
os.system("sudo pip install paste")
os.system("sudo pip install webapp2")
os.system("sudo pip install pycrypto")
os.system("sudo pip install jinja2")

#start webapp2 server
os.system("python " + os.path.join(os.path.dirname(__file__),"/home/piratectfrepository/piratectf/ubuntu_server/shellaccount_creationserver/main.py")) #starts webapp2 shell account creation server

#Configure message of the day
os.system("sudo cp " + os.path.join(os.path.dirname(__file__),"/home/piratectfrepository/piratectf/miscellaneous_files/motd") + " /etc/motd")
os.system("sudo chmod -x /etc/update-motd.d/*")

#install shellinabox and configure it
os.system("sudo apt-get install -y shellinabox")
#configure shellinabox, if necessary

#set up some things for user accounts
os.system("sudo groupadd pirates")
os.system("sudo useradd -G ctf2015teams -p " + encrypt("masterpiratepassword") + " masterpirate") #might need this, don't need it right now. I just added it just for fun.

#copy problems from shell_problems folder to the /home directory
os.system("sudo cp -r " + os.path.join(os.path.dirname(__file__),"/home/piratectfrepository/piratectf/ubuntu_server/shell_problems") + " /home/problems/")

#create problemsu group, create user in problemsu for each binary exploit problem
os.system("sudo addgroup problemsu")
os.system("sudo useradd -G problemsu -p " + encrypt("problemsensei") + " problemsensei") #The OP problem sensei. Will probably never need this account but its fun to add stuff in like this.

#set up permissions for each problem folder
for dirname,dirs,files in os.walk("/home/problems"):
	path = "/home/problems" + dirname
	username = name + "_probsu"
	os.system("sudo useradd -G problemsu -p " + encrypt(name + "password") + " " + username)
	os.system("sudo chown -hR " + username + ":problemsu " + path)
	os.system("sudo chmod -R 1600 " + path + "/flag")
	os.system("sudo chmod -R 5755 " + path + "/executable")
	os.system("sudo chmod -R 1744 " + path + "/source") 

#on a random note, its insane how much the "os" module can do. It literally set up the entire system for me!