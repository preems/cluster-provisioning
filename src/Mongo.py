from SshLib import SshConnection
import time

def installMongoDB(masterCons, configCons, shardCons):
	# con.run("sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10")
	# con.run('echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list')
	# con.run("sudo apt-get update")
	# con.run("sudo apt-get install -y mongodb-org")
	# con.run("sudo service mongod start")

	# configIPs = ["45.55.146.195"]
	# shardIPs = ["104.236.65.155", "104.131.90.33"]
	configIPs = []
	shardIPs = []
	# Install mongodb on all machines - START

	print "Performing mongo installation on master app servers"
	for master in masterCons:
		master.connect()
		master.run("sudo apt-get update")
		master.run("sudo apt-get -y install build-essential")
		master.run("sudo apt-get -y install mongodb")
		master.close()

	print "\nPerforming mongo installation on config servers"
	for config in configCons:
		config.connect()
		config.run("sudo apt-get update")
		config.run("sudo apt-get -y install build-essential")
		config.run("sudo apt-get -y install mongodb")
		config.run("sudo mkdir -p /data/db")
		config.run("sudo chmod 777 -R /data/db")
		config.run("sudo mkdir -p /data/configdb")
		config.run("sudo chmod 777 -R /data/configdb")
		configIPs.append(config.host)
		config.close()

	print "\nPerforming mongo installation on shard servers"
	for shard in shardCons:
		shard.connect()
		shard.run("sudo apt-get update")
		shard.run("sudo apt-get -y install build-essential")
		shard.run("sudo apt-get -y install mongodb")
		shard.run("sudo mkdir -p /data/db")
		shard.run("sudo chmod 777 -R /data/db")
		shardIPs.append(shard.host)
		shard.close()

	# Install mongodb on all machines - END

	# Run config server on config cons - START

	print "\nRunning Config servers"
	for config in configCons:
		config.connect()
		config.spawn('mongod --configsvr &')
		config.close()

	# Run config server on config cons - END

	# Run shard server on config cons - START

	print "\nRunning Shard servers"
	for shard in shardCons:
		shard.connect()
		shard.spawn("mongod --shardsvr &")
		shard.close()

	# Run shard server on config cons - END

	# Setup config and shard server IPs in Master App server - START

	mongosCmdString = "mongos --configdb "
	configIPsWithPorts = ""

	for configIP in configIPs:
		configIPsWithPorts = configIPsWithPorts + configIP + ":" + "27019" + ","

	configIPsWithPorts = configIPsWithPorts[:-1]
	mongosCmdString += configIPsWithPorts + " --port 27020 &"

	shardJSFileContents = ""
	for shardIP in shardIPs:
		shardJSFileContents += 'sh.addShard(\\"' + shardIP + ':27018\\")\n'

	shardJSFileContents += 'db.runCommand({enablesharding: \\"testDB\\"})\n'
	shardJSFileContents += 'sh.shardCollection(\\"testDB.testData\\", {\\"name\\":1})\n'
	shardJSFileContents += 'sh.status()\n'

	print "Waiting for Config and shard servers to start..."
	time.sleep(20)

	for master in masterCons:
		master.connect()
		master.spawn(mongosCmdString)
		master.run('touch $HOME/addShard.js')
		master.run('chmod 755 $HOME/addShard.js')
		master.run('echo "' + shardJSFileContents + '" >> $HOME/addShard.js')
		master.run('cat $HOME/addShard.js')
		master.run('mongo ' + master.host + ':27020/admin ' + ' < $HOME/addShard.js &')
		master.close()

	# Setup config and shard server IPs in Master App server - END


if __name__=="__main__":
	master = "45.55.156.25"
	config = "45.55.146.195"
	shards = ["104.236.65.155", "104.131.90.33"]

	masterCon = []
	masterCon.append(SshConnection(master, "root", useKey=True))
	configCon = []
	configCon.append(SshConnection(config, "root", useKey=True))
	shardCons = []

	for shard in shards:
		shardCon = SshConnection(shard, "root", useKey=True)
		shardCons.append(shardCon)

	installMongoDB(masterCon, configCon, shardCons)
