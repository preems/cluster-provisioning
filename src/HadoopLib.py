from SshLib import SshConnection
import os

def performHadoopOperations(con,type,master=None,slaves=None):
    ## need to change this. To read from config file
    HADOOP_USER_PASSWORD = "password"
    DOUBLE_PASSWORD = HADOOP_USER_PASSWORD+"\n"+HADOOP_USER_PASSWORD+"\n"
    hadoopUser = "hduser"
    noOfReplications = 2
    sshCommandString = "ssh -o StrictHostKeyChecking=no -t "

    hadoopCon = SshConnection(con.host, hadoopUser, password=HADOOP_USER_PASSWORD)
    hadoopCon.run('echo -e "\n" | ssh-keygen -t rsa -P ""')
    hadoopCon.run('cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys')
    if type == "master":
        hadoopCon.run(sshCommandString + 'master exit',password=HADOOP_USER_PASSWORD)
        hadoopCon.run(sshCommandString + '0.0.0.0 exit',password=HADOOP_USER_PASSWORD)
        hadoopCon.run('touch $HOME/login.expect')
        hadoopCon.run('chmod 755 $HOME/login.expect')
        hadoopCon.run('echo "spawn ssh-copy-id \$argv" >> $HOME/login.expect')
        hadoopCon.run('echo "expect ' + '\\"' + '*?(yes/no)' + '\\"' + '" >> $HOME/login.expect')
        hadoopCon.run('echo "send ' + '\\"' + 'yes' + '\\r\\"' + '" >> $HOME/login.expect')
        hadoopCon.run('echo "expect ' + '\\"' + '*?password' + '\\"' + '" >> $HOME/login.expect')
        hadoopCon.run('echo "send ' + '\\"' + HADOOP_USER_PASSWORD + '\\n\\"' + '" >> $HOME/login.expect')
        hadoopCon.run('echo "expect eof" >> $HOME/login.expect')

        for i in range(len(slaves)):
            slaveName = "slave" + str(i)
            hadoopCon.run('expect login.expect ' + hadoopUser + '@' + slaveName)
            hadoopCon.run(sshCommandString + slaveName + ' exit', password="yes")
    else:
        hadoopCon.run(sshCommandString + 'localhost exit',password=HADOOP_USER_PASSWORD)
        hadoopCon.run(sshCommandString + '0.0.0.0 exit',password=HADOOP_USER_PASSWORD)

    hadoopCon.run('curl -O http://mirror.cogentco.com/pub/apache/hadoop/core/stable/hadoop-2.6.0.tar.gz')
    hadoopCon.run('tar zxf hadoop*')
    hadoopCon.run('mv hadoop-2.6.0 hadoop')
    hadoopCon.run('echo "export HADOOP_HOME=$HOME/hadoop" >> $HOME/.bashrc')
    hadoopCon.run('echo "export JAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64" >> $HOME/.bashrc')
    hadoopCon.run('echo "export PATH=$PATH:$HADOOP_HOME/bin" >> $HOME/.bashrc')

    if type == "master":
        hadoopCon.run('echo master > $HOME/hadoop/etc/hadoop/slaves')
        for i in range(len(slaves)):
            slaveName = "slave" + str(i)
            hadoopCon.run('echo ' + slaveName + ' >> $HOME/hadoop/etc/hadoop/slaves')

    updateHadoopConfigurationFiles(hadoopCon, noOfReplications)

    if type == "master":
        hadoopCon.run('$HOME/hadoop/bin/hadoop namenode -format',password="Y")
        hadoopCon.run('$HOME/hadoop/sbin/start-dfs.sh', password="yes" + "\n" + "yes")
        # hadoopCon.run('$HOME/hadoop/sbin/start-yarn.sh', password="yes")
        hadoopCon.run('/usr/lib/jvm/java-6-openjdk-amd64/bin/jps')
        # hadoopCon.run('$HOME/hadoop/sbin/stop-dfs.sh', password="yes")
        # hadoopCon.run('$HOME/hadoop/sbin/stop-yarn.sh', password="yes")

def updateHadoopConfigurationFiles(hadoopCon, noOfReplications=2):
    ######Modify XML and config files of Hadoop
    hadoopCon.run("sed -i 's/#.?export JAVA_HOME/export JAVA_HOME=\/usr\/lib\/jvm\/java-6-openjdk-amd64/g' /home/hduser/hadoop/etc/hadoop/hadoop-env.sh")
    # #
    ###Adding temp directory path to core-site.xml - START
    hadoopCon.run("mkdir -p $HOME/hadoop-temp")
    hadoopCon.run("chown hduser:hadoop /$HOME/hadoop-temp")
    hadoopCon.run("chmod 750 /$HOME/hadoop-temp")
    #
    hadoopCon.run("sed -i 's/^<\/configuration>//g' /home/hduser/hadoop/etc/hadoop/core-site.xml")
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <name>hadoop.tmp.dir</name>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <value>$HOME/hadoop-temp/</value>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <description>A base for other temporary directories.</description>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <name>fs.default.name</name>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <value>hdfs://master:54310</value>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <description>The name of the default file system. </description>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "</configuration>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    # ###Adding temp directory path to core-site.xml - END
    #
    # ###Adding configuration to mapred-site.xml - START
    hadoopCon.run("mv $HOME/hadoop/etc/hadoop/mapred-site.xml.template $HOME/hadoop/etc/hadoop/mapred-site.xml")
    hadoopCon.run("sed -i 's/^<\/configuration>//g' /home/hduser/hadoop/etc/hadoop/mapred-site.xml")
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "  <name>mapred.job.tracker</name>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "  <value>master:54311</value>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "  <description>The host and port that the MapReduce job tracker runs at.</description>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "</configuration>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    ###Adding configuration to mapred-site.xml - END

    ###Adding configuration to hdfs-site.xml - START
    hadoopCon.run("sed -i 's/^<\/configuration>//g' /home/hduser/hadoop/etc/hadoop/hdfs-site.xml")
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "  <name>dfs.replication</name>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "  <value>' + str(noOfReplications) + '</value>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "  <description>Default block replication.</description>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "</configuration>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    # Adding configuration to hdfs-site.xml - END

def performRootoperations(con, type=type, master=None, slaves=None):
    ## need to change this. To read from config file
    HADOOP_USER_PASSWORD = "password"
    DOUBLE_PASSWORD = HADOOP_USER_PASSWORD+"\n"+HADOOP_USER_PASSWORD+"\n"
    hadoopUser = "hduser"

    con.run("sudo apt-get update")
    con.run("sudo apt-get -y install python-software-properties")
    con.run("sudo add-apt-repository ppa:ferramroberto/java")
    con.run("sudo apt-get -y install openjdk-6-jdk")
    con.run("sudo update-java-alternatives -s java-6-sun")
    con.run("java -version")
    con.run("sudo addgroup hadoop")
    con.run('echo -e "'+DOUBLE_PASSWORD+'" | sudo adduser --ingroup hadoop ' + hadoopUser)
    con.run('echo "JAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64" >> /etc/environment')
    if type == "master":
        con.run("sudo apt-get -y install expect")

    updateHostsFile(con, type=type, master=master, slaves=slaves)

def updateHostsFile(con, type="master", master=None, slaves=None):
    if type == "master":
        if slaves is None:
            print "Please provide IP addresses of the slave machines"
            return
        con.run('echo "' + con.host +'\tmaster" >> /etc/hosts')
        for i in range(len(slaves)):
            slaveName = "slave" + str(i)
            con.run('echo "' + slaves[i] +'\t' + slaveName +'" >> /etc/hosts')
    else:
        if master is None:
            print "Please provide IP addresses of the master machine"
            return
        con.run('echo "' + master +'\tmaster" >> /etc/hosts')
        con.run('echo "' + con.host +'\t' + type +'" >> /etc/hosts')

    con.run('echo "sshd: ALL" >> /etc/hosts.allow')

def installHadoop(master,slaves):
    masterIP = master.host
    slavesIP = []
    for i in range(len(slaves)):
        slavesIP.append(slaves[i].host)

    print "\nPerforming root operations on master"
    performRootoperations(master, type="master", slaves=slavesIP)

    print "\nPerforming root operations on slaves"
    for i in range(len(slaves)):
        slaveName = "slave" + str(i)
        performRootoperations(slaves[i], type=slaveName, master=masterIP)

    print "\nPerforming hadoop operations on slaves"
    for i in range(len(slaves)):
        slaveName = "slave" + str(i)
        print "Operations on " + slaveName
        performHadoopOperations(slaves[i], slaveName, master=masterIP)

    print "\nPerforming hadoop operations on master"
    performHadoopOperations(master, type="master", slaves=slavesIP)

if __name__ == '__main__':
    master = "45.55.189.91"
    slaves = ["45.55.190.100", "45.55.173.111", "104.236.38.238", "104.236.213.5"]

    print "\nPerforming root operations on master"
    con = SshConnection(master, "root", useKey=True)
    performRootoperations(con, type="master", slaves=slaves)

    print "\nPerforming root operations on slaves"
    for i in range(len(slaves)):
        slaveName = "slave" + str(i)
        con = SshConnection(slaves[i], "root", useKey=True)
        performRootoperations(con, type=slaveName, master=master)

    print "\nPerforming hadoop operations on slaves"
    for i in range(len(slaves)):
        slaveName = "slave" + str(i)
        print "Operations on " + slaveName
        con = SshConnection(slaves[i], "root", useKey=True)
        performHadoopOperations(con, slaveName, master=master)

    print "\nPerforming hadoop operations on master"
    con = SshConnection(master, "root", useKey=True)
    performHadoopOperations(con, type="master", slaves=slaves)
