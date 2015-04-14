import requests
from requests.exceptions import ConnectionError
from SshLib import SshConnection
import json
import paramiko
import time
import os
import SshLib
from config import Configuration


DO_PUBLICKEY=None
DO_PUBLICKEYID=None


"""
def createKeyInDo():
	#data={'name':'Generated SSH Key','public_key':'ssh-rsa '+paramiko.RSAKey.generate(1024).get_base64().encode('ascii','ignore')+' example'}
	data={'name':'Generated SSH Key','public_key':"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqKn5pT/0C5OK+nXQce9jGqZOnd9vhB8GKJ8aPXFlQbojtVvMXIJQ5o/mF39ij+UccDKLKKJdKd5eCw6vb5PJuPw2M+f3M7DNeASSAaq9h32rEk4GOHzRP9u5cSdcadsrAMFjt0yFFrtaGFsw9DKmKp3t/ofUovI1AkBDmPRqG2TF00cxeCApTOZevXkLLuVJCsdhwxtu1J4jmKwAy+3/k0e+trb2Z40ZUxXREf1N55aP58bAJOLzmg+HyfKo/ztFSoyHqR2bXpNzCArUirUIWu9DNih6JkPOWbWgVYJiCd+Ljc/nPdU6/sKEv9am630X725512jGmn+P4H5cnvHiP preems@Preethams-MacBook-Pro.local"}
	try:
		response = requests.post(DO_APIHOST+'account/keys',data=json.dumps(data),headers=headers)
	except ConnectionError:
		print "Error: Unable to Connect to Digital Ocean"
		exit()

	response = json.loads(response.text)
	print response['ssh_key']['id']
	#exit()
	return response['ssh_key']['id']
"""

def initDO(conf):
	addPublicKeytoDO(conf)

def addPublicKeytoDO(conf):
	global DO_PUBLICKEYID
	if DO_PUBLICKEY==None:
		setPublicKey()

	#headers={'Content-Type':'application/json', 'Authorization': 'Bearer '+conf.get("DO_AUTHKEY")}
	headers={'Content-Type':'application/json', 'Authorization': 'Bearer '+DO_AUTHKEY}

	if DO_PUBLICKEYID==None:
		#Check weather the key is already added to the DO
		try:
			response=requests.get(conf.get("DO_APIHOST")+"account/keys",headers=headers)
		except ConnectionError:
			print "Error: Unable to Connect to Digital Ocean"
			exit()
		response=json.loads(response.text)
		if "ssh_keys" not in response:
			print "Error: Digital Ocean access denied: "+str(response)
			print "headers: "+str(headers)
			exit()
		for i in response["ssh_keys"]:
			if i["public_key"].encode('ascii','ignore').strip()==DO_PUBLICKEY.encode('ascii','ignore').strip():
				print "Key already present in DigitalOcean"
				DO_PUBLICKEYID=i["id"]
				return
		#if key not found, add it to the list in Digital Ocean
		data={'name':'Generated SSH Key','public_key':DO_PUBLICKEY}
		try:
			response = requests.post(conf.get("DO_APIHOST")+'account/keys',data=json.dumps(data),headers=headers)
		except ConnectionError:
			print "Error: Unable to Connect to Digital Ocean"
			exit()
		response=json.loads(response.text)
		print response
		DO_PUBLICKEYID=response["ssh_key"]["id"]

def setPublicKey():
	global DO_PUBLICKEY
	with open(os.environ["HOME"]+"/.ssh/id_rsa.pub") as keyfile:
		publicKey = keyfile.readlines()
	DO_PUBLICKEY=publicKey[0]

class Droplet(object):


	def __init__(self,conf):
		self.ip=None
		self.size=conf.get("DO_INSTANCE_TYPE")
		self.id=None
		self.sshKeyId=DO_PUBLICKEYID
		self.headers={'Content-Type':'application/json', 'Authorization': 'Bearer '+conf.get("DO_AUTHKEY")}

		
		data={'name':'example.com','region':conf.get("DO_REGION"),'size':self.size,'image':conf.get("DO_IMAGE"),'backups':'false','ipv6':'true','ssh_keys':[self.sshKeyId]}
		try:
			response = requests.post(conf.get("DO_APIHOST")+'droplets',data=json.dumps(data),headers=self.headers)
		except ConnectionError:
			print "Error: Unable to Connect to Digital Ocean"
			exit()

		try:
			response = json.loads(response.text)
			self.id=response['droplet']['id']
			self.status=response['droplet']['status']
		except:
			print "Error: Creation of droplet in Digital Ocean failed"
			print response
			exit()

		while True:
			time.sleep(1)
			try:
				response=requests.get(conf.get("DO_APIHOST")+'droplets/'+str(self.id),headers=self.headers)
			except ConnectionError:
				print "Error: Unable to connect to Digital Ocean"
				exit()

			response=json.loads(response.text)
			if len(response['droplet']['networks']['v4'])>0:
				break
		self.ip=response['droplet']['networks']['v4'][0]['ip_address']

	def isActive(self):
		try:
			response = requests.get(conf.get("DO_APIHOST")+'droplets/'+str(self.id),headers=self.headers)
		except ConnectionError:
			print "Error: Unable to connect "

		response = json.loads(response.text)
		if response['droplet']['status']=='active':
			return True
		else:
			return False

	def fetchIp(self):
		if self.ip!=None:
			return self.ip

	def getConnection(self):
		return SshConnection(self.ip,"root",useKey=True)

	def getIP(self):
		return self.ip

if __name__=='__main__':
	conf = Configuration("cat.conf")
	initDO(conf)
	d=Droplet(conf)
	print "Created a VM with id ",d.id," and IP address ",d.ip," and SSH key id",d.sshKeyId
	while not d.isActive():
		print "Waiting for VM to boot..."
		time.sleep(5)
	print "VM is active"
	time.sleep(10)
	con=d.getConnection()
	con.run("pwd")