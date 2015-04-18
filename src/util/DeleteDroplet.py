import requests
from requests.exceptions import ConnectionError
import sys
sys.path.append("../")
from config import Configuration
import json



conf = Configuration("../cat.conf")
headers={'Content-Type':'application/json', 'Authorization': 'Bearer '+conf.get("DO_AUTHKEY")}
response=requests.get(conf.get("DO_APIHOST")+"droplets",headers=headers)
print response.text
response = json.loads(response.text)

for droplets in response['droplets']:
	res = requests.delete(conf.get("DO_APIHOST")+'droplets/'+droplets['id'])
	print res