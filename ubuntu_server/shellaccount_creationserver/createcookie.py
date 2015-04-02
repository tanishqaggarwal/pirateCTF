import json
from securefunctions import *

def main():
	print "This script produces cookies from a teamname provided."
	encrypted_text = encrypt("n0t_sh@d1er_th@n_sh@n!sh" + raw_input("Enter a teamname to encrypt: "))
	print "Encrypted text: " + encrypted_text

if __name__ == "__main__":
	main()