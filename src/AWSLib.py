from SshLib import SshConnection
import boto.ec2
from config import Configuration
import os,time

class AWSInstance(object):
    def __init__(self,conf):
        self.ip=None
        self.reservation=None
        self.id=None
        #Connecting
        print "Connecting to AWS Cloud..."
        self.conn = boto.ec2.connect_to_region(conf.get("AWS_REGION"),aws_access_key_id=conf.get("AWS_ACCESS_KEY"),aws_secret_access_key=conf.get("AWS_SECRET_KEY"))

        #Adding key
        print "Adding the key to AWS..."
        try:
            with open(os.environ['HOME']+"/.ssh/id_rsa.pub") as kfile:
                key = kfile.read()
                key_pair=self.conn.import_key_pair('cat_key',key)
                print "Key pair registered to Amazon"
        except boto.exception.EC2ResponseError:
            print "Key already registered in Amazon"

        #Creating Instance
        print "Creating VM Instance..."
        reservation = self.conn.run_instances(conf.get("AWS_UBUNTU_AMI"), key_name='cat_key',instance_type=conf.get("AWS_INSTANCE_TYPE"), security_groups=[conf.get("AWS_SECURITY_GROUP")])
        self.reservation=reservation
        self.id=reservation.instances[0].id
        print self.id

    def fetchIp(self):
        for r in self.conn.get_all_instances():
            if r.id == self.reservation.id:
                break
        self.ip = r.instances[0].ip_address
        return self.ip

    def  getIp(self):
        return self.ip

    def isActive(self,conf):
        return True

    def getConnection(self):
        return SshConnection(self.ip,"ubuntu",useKey=True)


if __name__=='__main__':
    conf = Configuration("cat.conf")
    ins = AWSInstance(conf)
    time.sleep(5)
    print ins.fetchIp()
    time.sleep(70)
    con = ins.getConnection()
    #con = SshConnection("ec2-54-149-108-32.us-west-2.compute.amazonaws.com","ubuntu",useKey=True)
    con.run("pwd")
    con.run("sudo ls /")
