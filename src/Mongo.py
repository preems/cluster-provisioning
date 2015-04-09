from SshLib import SshConnection

def installMongoDB(con):
	con.run("sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10")
	con.run('echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list')
	con.run("sudo apt-get update")
	con.run("sudo apt-get install -y mongodb-org")
	con.run("sudo service mongod start")

if __name__=="__main__":

