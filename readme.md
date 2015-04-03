PirateCTF Platform
===================

Introduction
-------------------

Pirate CTF is a CTF competition hosted for high schoolers, by high schoolers.
This repository contains the code for the PirateCTF 2015 online competition, and can easily be generalized to adapt to most other CTF competitions.

Structure
--------------------

This repository is divided into four folders. 
- The first folder contains the appengine problem server, which hosts various web challenges and is NOT the scoring server. If you're implementing your own CTF, this folder can be deleted as it's pirateCTF-specific.
- The second folder contains the *appengine scoring server*, which is probably what you're concerned with mostly. It contains a Google App Engine Python 2.7 webapp2 application that can be run as-is and configured through a web browser.
- The third folder contains the *shell server implementation*, which includes a account creation Python service module. In this folder, setup.py sets up various things such as a shellinabox system for SSHing into the shell server.
- The fourth folder contains various documents related to pirateCTF 2015 problems, including skeletons of solutions, code and writeups. If you're implementing your own CTF, this folder can be deleted as it's pirateCTF-specific.

Usage
-------------------

### AppEngine Scoring Server

The appengine scoring server is well-documented with comments and is fairly self-explanatory. Set up an App Engine application, deploy it with the given code and it will run fine as-is. Your own custom stylings are easy to apply, and there is an admin console to facilitate most tasks.

If you're confused about the problem_parents and problem_children properties of the Problems model, we strongly encourage you to go to http://piratectf.com and check out our problem layout, and consider using it for your own CTF. If not, you have two options: either refactoring our code completely, or initializing the problem_parent to a list containing one element: the name of the previous problem and the problem_children to a list containing one element which is the name of the problem following after.

We also implement a mechanism where users can buy problem flags for points. To let this mechanism render no effect on scoring, you can set the problem buy point value to the same thing as the actual problem point value, so that any users that buy flags receive 0 points.

Finally, if you do not want your users to absolutely have to submit an explanation for every problem, you don't have to. Just remove it from the problems.html source code.

### Shell Server

To use the shell server, simply run setup.py in the ubuntu_server folder. 

#### Currently-known supported systems by setup.py
The following is a list of systems that are currently known to work with setup.py in the ubuntu_server folder. If you find that the script works in other Ubuntu distributions, please contact us to update this readme. Note that the below list applies only to clean installations.

- Ubuntu Server 14.04

Contributions
-------------------

To contribute to this project, just fork from it.

License
-------------------

All of the above content is now licensed under the MIT license. A copy of the license can be found in license.md.