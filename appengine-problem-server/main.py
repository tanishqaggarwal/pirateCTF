#PirateCTF 2015 AppEngine problem server.

import webapp2
from mainpageserver import *
from fishycookies import *
from deminification import *

application = webapp2.WSGIApplication([
    #mainpageserver.py
    ('/', Index),
    #fishy cookies problem -- fishycookies.py
    ('/fishy_cookies',FishyCookiesLogin),
    ('/chondrichthyes_admin',FishyCookiesAdmin),
    ('/no_fish_for_you',FishyCookiesNoAdmin),
    ('/the_KEY_to_fishy_success',FishyCookiesEncryptionDecryption),
    #deminification exercise -- deminification.py
    ('/deminification-exercise',DeminificationExercise),
    ('/dmf',RequestDeminificationFlag),
    #injection 1 -- injection2.py
    ('/injection1',InjectionOne),
    ('/injection1admin',InjectionOneAdmin),
    #
], debug=True)