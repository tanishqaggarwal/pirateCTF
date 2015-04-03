#PirateCTF 2015 AppEngine platform.
#This software platform is distributed under the MIT license. A copy of the license can be found in license.md.

import hmac
import base64
from Crypto.Cipher import AES
from Crypto import Random

ENCRYPTION_SECRET = "P!r@teCtF__sh@dy"
PASS_HASH_SECRET = "n0t_sh@d1er_th@n_sh@n!sh"

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class AES_Cipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) ) 

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))

def encrypt(theinformation):
	my_AES = AES_Cipher(ENCRYPTION_SECRET)
	return my_AES.encrypt(theinformation)
	
def decrypt(thecookie):
	my_AES = AES_Cipher(ENCRYPTION_SECRET)
	return my_AES.decrypt(thecookie)
	
def hash_pass(pass_string):
	return hmac.new(PASS_HASH_SECRET, pass_string).hexdigest()

def return_pass_hash_secret():
	return PASS_HASH_SECRET

def return_github_oauth_token():
    return GITHUB_OAUTH_TOKEN

def return_github_username():
    return GITHUB_USERNAME

def return_admin_password():
    return ADMIN_PASSWORD