from SshLib import SshConnection

def installHadoop(con,type):

    ## need to change this. To read from config file
    HADOOP_USER_PASSWORD = "password"
    DOUBLE_PASSWORD = HADOOP_USER_PASSWORD+"\n"+HADOOP_USER_PASSWORD+"\n"
    hadoopUser = "hduser"

    con.run("sudo apt-get update")
    con.run("sudo apt-get -y install python-software-properties")
    con.run("sudo add-apt-repository ppa:ferramroberto/java")
    con.run("sudo apt-get -y install openjdk-6-jre")
    con.run("sudo update-java-alternatives -s java-6-sun")
    con.run("java -version")
    con.run("sudo addgroup hadoop")
    con.run('echo -e "'+DOUBLE_PASSWORD+'" | sudo adduser --ingroup hadoop ' + hadoopUser)

    hadoopCon = SshConnection(con.host, hadoopUser, password=HADOOP_USER_PASSWORD)
    hadoopCon.run('echo -e "\n" | ssh-keygen -t rsa -P ""')
    hadoopCon.run('cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys')
    hadoopCon.run('ssh -t localhost exit',password="yes")
    hadoopCon.run('curl -O http://mirror.cogentco.com/pub/apache/hadoop/core/stable/hadoop-2.6.0.tar.gz')
    hadoopCon.run('tar zxf hadoop*')
    hadoopCon.run('mv hadoop-2.6.0 hadoop')
    hadoopCon.run('echo "export HADOOP_HOME=$HOME/hadoop" >> $HOME/.bashrc')
    hadoopCon.run('echo "export JAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64" >> $HOME/.bashrc')
    hadoopCon.run('echo "export PATH=$PATH:$HADOOP_HOME/bin" >> $HOME/.bashrc')


    ######Modify XML and config files of Hadoop
    hadoopCon.run("sed -i 's/#.?export JAVA_HOME/export JAVA_HOME=\/usr\/lib\/jvm\/java-6-openjdk-amd64/g' /home/hduser/hadoop/etc/hadoop/hadoop-env.sh")

    ###Adding temp directory path to core-site.xml - START
    hadoopCon.run("mkdir -p $HOME/hadoop-temp")
    hadoopCon.run("chown hduser:hadoop /$HOME/hadoop-temp")
    hadoopCon.run("chmod 750 /$HOME/hadoop-temp")

    hadoopCon.run("sed -i 's/^<\/configuration>//g' /home/hduser/hadoop/etc/hadoop/core-site.xml")
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <name>hadoop.tmp.dir</name>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <value>$HOME/hadoop-temp/</value>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <description>A base for other temporary directories.</description>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <name>fs.default.name</name>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <value>hdfs://localhost:54310</value>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "  <description>The name of the default file system. </description>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/core-site.xml')
    hadoopCon.run('echo "</configuration>" >> $HOME/hadoop/etc/hadoop/core-site.xml')

    ###Adding temp directory path to core-site.xml - END

    ###Adding configuration to mapred-site.xml - START
    hadoopCon.run("mv $HOME/hadoop/etc/hadoop/mapred-site.xml.template $HOME/hadoop/etc/hadoop/mapred-site.xml")
    hadoopCon.run("sed -i 's/^<\/configuration>//g' /home/hduser/hadoop/etc/hadoop/mapred-site.xml")
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "  <name>mapred.job.tracker</name>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "  <value>localhost:54311</value>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "  <description>The host and port that the MapReduce job tracker runs at.</description>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    hadoopCon.run('echo "</configuration>" >> $HOME/hadoop/etc/hadoop/mapred-site.xml')
    ###Adding configuration to mapred-site.xml - END

    ###Adding configuration to hdfs-site.xml - START
    hadoopCon.run("sed -i 's/^<\/configuration>//g' /home/hduser/hadoop/etc/hadoop/hdfs-site.xml")
    hadoopCon.run('echo "<property>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "  <name>dfs.replication</name>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "  <value>1</value>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "  <description>Default block replication.</description>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "</property>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    hadoopCon.run('echo "</configuration>" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml')
    ###Adding configuration to hdfs-site.xml - END
