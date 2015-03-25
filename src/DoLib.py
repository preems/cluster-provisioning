import requests
from requests.exceptions import ConnectionError
import json
import paramiko
import time

DO_REGION='nyc3'
DO_IMAGE='ubuntu-14-04-x64'
DO_AUTHKEY='f414f89482ce1a12ee202c24c06111876bb0cc62f5129023c1be98717f0483b4'
DO_APIHOST='https://api.digitalocean.com/v2/'

#TODO Get Authkey from config class
headers={'Content-Type':'application/json', 'Authorization': 'Bearer '+DO_AUTHKEY}

ramSizeToDoSizeMap={}
ramSizeToDoSizeMap[512]='512mb'
ramSizeToDoSizeMap[1024]='1gb'

def createKeyInDo():
	data={'name':'Generated SSH Key','public_key':'ssh-rsa '+paramiko.RSAKey.generate(1024).get_base64().encode('ascii','ignore')+' example'}
	try:
		response = requests.post(DO_APIHOST+'account/keys',data=json.dumps(data),headers=headers)
	except ConnectionError:
		print "Error: Unable to Connect to Digital Ocean"
		exit()

	print response.text
	response = json.loads(response.text)
	print response['ssh_key']['id']
	#exit()
	return response['ssh_key']['id']

class Droplet(object):
	def __init__(self,size):
		self.ip=None
		self.size=ramSizeToDoSizeMap[size]
		self.id=None
		self.sshKeyId=createKeyInDo()

		data={'name':'example.com','region':DO_REGION,'size':self.size,'image':DO_IMAGE,'backups':'false','ipv6':'true','ssh_keys':[self.sshKeyId]}
		try:
			response = requests.post(DO_APIHOST+'droplets',data=json.dumps(data),headers=headers)
		except ConnectionError:
			print "Error: Unable to Connect to Digital Ocean"
			exit()
		print response.text
		response = json.loads(response.text)
		self.id=response['droplet']['id']
		self.status=response['droplet']['status']

		while True:
			time.sleep(1)
			try:
				response=requests.get(DO_APIHOST+'droplets/'+str(self.id),headers=headers)
			except ConnectionError:
				print "Error: Unable to Connect to Digital Ocean"
				exit()

			response=json.loads(response.text)
			if len(response['droplet']['networks']['v4'])>0:
				break
		self.ip=response['droplet']['networks']['v4'][0]['ip_address']

	def isActive(self):
		try:
			response = requests.get(DO_APIHOST+'droplets/'+str(self.id),headers=headers)
		except ConnectionError:
			print "Error: Unable to Connect "

		response = json.loads(response.text)
		if response['droplet']['status']=='active':
			return True
		else:
			return False


if __name__=='__main__':
	d=Droplet(512)
	print d.id
	print d.ip

	while not d.isActive():
		print "Waiting for VM to boot..."
		time.sleep(5)
	print "VM is active"