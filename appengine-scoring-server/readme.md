AppEngine Scoring Server
===============================

Quickstart
------------------------------------------

This is the part you're probably most concerned with if you're looking to host a CTF. 

If you want to quickstart, all you have to do is edit the parameters of your choosing in main.py, and most things will work on their own. Styling is pretty simple; templates are found in the `html` folder and all the includes (navbar, css, js, etc.) are all found in the `static` folder.

_One very important thing to change is `securefunctions.py`_. Make sure to change your secrets so that, if anyone competing in your CTF figures out that you're using our platform, they can't impersonate other teams by creating their own cookies. (In practice it shouldn't be possible anyway to impersonate other teams even through cookie stealing since Google authentication is necessary, but its always good to have multiple barriers of defense).

File/Folder Descriptions
-------------------------------------------

### Folders

The `static` and `html` folders both contain static content served to end users, and the file names are descriptive and self-explanatory. Note that `*.html` is a whitespace-stripped version of the html content that is sent to the user; it is recommended that you minify any changes to a `*.full.html` template and copy them over into the corresponding `*.html` file. Also, `html/development` contains templates used through the development server when testing.

The `lib` folder is a remnant of an attempt to install marshal. Doesn't contain anything. You could probably delete `appengine_config.py` and `lib` together if you want.

### Files

`db.py` contains the Model definitions for the datastore.

`securefunctions.py`, as mentioned above, is critically important. Make sure you change the key from what's in this repository. Note that the `PASS_HASH_SECRET` isn't as critical to change; all of the hashes are publicly viewable and are just used to identify problems and updates.

`main.py` is the boring, main application script and pulls all of the handler definitions from `pageserver.py`, `securefunctions.py`, `development.py`, and `grader.py`. This is also where you might want to make parameter changes for your specific needs.

`pageserver.py` contains a bulk of the backend and displays most of the important pages. The code is (hopefully) well-documented enough for you to understand, so dive right in if you feel like you need to change something!

`grader.py` contains mechanisms to grade/buy problem flags. It's pretty rudimentary stuff and can probably be used as-is. Note that if you want to disable the problem hierarchy/buying feature, do so through `main.py`, not by deleting corresponding `grader.py` code.