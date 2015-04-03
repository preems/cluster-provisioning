

class Configuration(object):
	_map={}
	DO_requiredValues=["DO_REGION","DO_IMAGE","DO_AUTHKEY","DO_APIHOST"]
	HADOOP_requiredValues=[]
	def __init__(configfile="../cat.conf"):
		with open(configfile) as cfile:
			for line in cfile:
				if line[0]=='#' or line[0]=' ':
					continue
				else:
					pair = line.split("=")
					_map[pair[0]]=pair[1]


	def getValue(key):
		if key in _map:
			return _map[key]
		else:
			return False


	def _validate(requiredValues):
		for i in requiredValues:
			if i not in _map:
				return False
		return True

	def DOValidate():
		return _validate(DO_requiredValues)

	def HADOOPValidate():
		return _validate(HADOOP_requiredValues)