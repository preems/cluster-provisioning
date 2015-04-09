from config import Configuration
from DoLib import Droplet
from SshLib import SshConnection


def initConfig():
	conf = Configuration("cat.conf")
	if conf.DOValidate():
		print "Digital Ocean config validated"
	else:
		print "Error: Please enter all required values for Digital Ocean"

	if conf.HADOOPValidate():
		print "Hadoop config validated"
	else:
		print "Error: Please enter all required values for Hadoop"

	return conf






