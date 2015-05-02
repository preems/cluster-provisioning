from config import Configuration
from DoLib import Droplet,initDO
from SshLib import SshConnection
from AWSLib import AWSInstance
from HadoopLib import installHadoop
from Mongo import installMongoDB
from OpenstackLib import openStackInstance
import argparse
import time

#import openstack
OpenStackInstance=None

APP_CHOICES=['hadoop','mongodb','none']
PROVIDER_CHOICES=['digitalocean','openstack','aws']

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

	if conf.AWSValidate():
		print "Amazon AWS config validated"
	else:
		print "Error: Please enter all required values for Amazon AWS"
	return conf

def createInstances(nodes,CloudProvider,providerName,conf):
	instances=[]
	print "Creating ",nodes," instances on ",providerName,"....."
	for i in range(nodes):
		instances.append(CloudProvider(conf))
		time.sleep(5)
		print "Instance created with ip/hostname ",instances[-1].fetchIp()

	print "Waiting for all the instances to boot..."
	time.sleep(90)

	while True:
		if instances[-1].isActive(conf):
			break
		time.sleep(5)
	time.sleep(30)
	return instances

if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Automates provisioning of Hadoop and MongoDB clusters on platforms like Digital Ocean, Amazon Web Services and Open Stack')
	parser.add_argument('--nodes',dest='nodes',default=1,type=int,help="Number of nodes in the cluster. Default is 1")
	parser.add_argument('--app',dest='app',required=True,type=str,nargs='?',choices=APP_CHOICES,help="Application to be installed")
	parser.add_argument('--provider',dest='provider',required=True,type=str,nargs='?',choices=PROVIDER_CHOICES,help='Choose the Cloud provider')

	args=parser.parse_args()
	#print args.nodes
	#print args.app
	#print args.provider

	conf = initConfig()

	if args.provider=='digitalocean':
		CloudProvider=Droplet
		initDO(conf)
	elif args.provider=='aws':
		CloudProvider=AWSInstance
	elif args.provider=='openstack':
		CloudProvider=openStackInstance


	instances=createInstances(args.nodes,CloudProvider,args.provider,conf)

	if args.app=='none':
		print "All VMs created and ready for use"
		for i in instances:
			print i.getIP()
		exit()

	if args.app=='hadoop':
		master=instances[0].getConnection()
		slaves=[]
		if args.nodes>1:
			for i in range(1,args.nodes):
				slaves.append(instances[i].getConnection())

		installHadoop(master,slaves,conf)

		print "*********************** Hadoop Installation Complete **************************"
		print
		print "Hadoop Cluster Details:"
		print "Name Node: ",master.host
		for i in slaves:
			print "Data Node:",i.host

	if args.app=='mongodb':
		shard=[]
		master = []
		config =[]
		master.append(instances[0].getConnection())
		config.append(instances[1].getConnection())

		for i in range(2,args.nodes):
			shard.append(instances[i].getConnection())

		installMongoDB(master,config,shard)

		print "*********************** MongoDB Installation Complete **************************"
		print
		print 'MongoDB Cluster Details:'
		print "App node: "+master[0].host
		print "Config node: "+config[0].host
		for i in shard:
			print "Shard nodes: "+i.host
