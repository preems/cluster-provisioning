

class Configuration(object):
	_map={}
	DO_requiredValues=["DO_REGION","DO_IMAGE","DO_AUTHKEY","DO_APIHOST"]
	HADOOP_requiredValues=["HADOOP_USER_NAME","HADOOP_USER_PASSWORD"]
	def __init__(self,configfile="../cat.conf"):
		with open(configfile) as cfile:
			for line in cfile:
				if line[0]=='#' or line[0]==' ':
					continue
				else:
					pair = line.split("=")
					self._map[pair[0].strip()]=pair[1].strip()


	def get(self,key):
		if key in self._map:
			return str(self._map[key])
		else:
			return False


	def _validate(self,requiredValues):
		for i in requiredValues:
			if i not in self._map:
				return False
		return True

	def DOValidate(self):
		return self._validate(self.DO_requiredValues)

	def HADOOPValidate(self):
		return self._validate(self.HADOOP_requiredValues)

if __name__ == '__main__':
	conf = Configuration("cat.conf")
	print conf.DOValidate()
	print conf.HADOOPValidate()
	print conf.getValue("DO_APIHOST")
	print conf.getValue("DO_IMAGE")