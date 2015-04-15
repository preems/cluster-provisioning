import os, time
import keystoneclient.v2_0.client as keystoneclient
import novaclient.v1_1.client as novaclient
from SshLib import SshConnection
from config import Configuration

class openStackInstance(object):
    def get_keystone_creds(self,conf):
        d = {}
        d['username'] = conf.get('OS_USERNAME')
        d['password'] = conf.get('OS_PASSWORD')
        d['auth_url'] = conf.get('OS_AUTH_URL')
        d['tenant_name'] = conf.get('OS_TENANT_NAME')
        return d

    def get_nova_creds(self, conf):
        d = {}
        d['username'] = conf.get('OS_USERNAME')
        d['api_key'] = conf.get('OS_PASSWORD')
        d['auth_url'] = conf.get('OS_AUTH_URL')
        d['project_id'] = conf.get('OS_TENANT_NAME')
        return d

    def __init__(self,conf):
        self.ip = None
        self.name = None
        self.id = None
        self.instance = None
        self.keystonecredential = self.get_keystone_creds(conf)
        self.novacredentials = self.get_nova_creds(conf)
        self.image_name = conf.get('IMAGE_NAME')
        self.flavor = conf.get('FLAVOR_NAME')
        print 'Attempting keystone authentication'
        self.keystoneobj = keystoneclient.Client(**self.keystonecredential)
        if self.keystoneobj.authenticate() == False:
            print "Unable to authenticate keystone credentials"
            return
        print 'keystone authentication successfull'
        print 'Creating an object for nova'
        self.novaobj = novaclient.Client(**self.novacredentials)

        # Section to setup keys in openstack environment
        keyname = os.environ['USER']
        if len(self.novaobj.keypairs.list()) == 0:
            print 'Copying ssh public key'
            self.novaobj.keypairs.create(name=keyname+'1', public_key=open(os.path.expanduser('~/.ssh/id_rsa.pub')).read())
            keyname = keyname+str(1)
        else:
            isMyKeyPresent = False
            print 'Checking existant ssh keys'
            try:
                mypublickey = open(os.path.expanduser('~/.ssh/id_rsa.pub')).read().strip()
                index = 0
                for eachkey in self.novaobj.keypairs.list():
                    index += 1
                    if (eachkey.public_key.strip() == mypublickey):
                        keyname = eachkey.name
                        isMyKeyPresent = True
                        break
                if isMyKeyPresent == False:
                    print 'Adding public key to openstack'
                    keyname = keyname + str(index+1)
                    self.novaobj.keypairs.create(name=keyname, public_key=open(os.path.expanduser('~/.ssh/id_rsa.pub')).read())
            except:
                print 'Caught exception while trying to add key to server. Possible that tried to add a duplicate key'
        # Section to determine image to load
        imageExists = False
        available_images = self.novaobj.images.list()
        for index in range(1,len(available_images)+1):
            if repr(available_images[index-1].name.lower()).find(self.image_name) != -1:
                self.image_name = available_images[index-1]
                imageExists = True
                break
        if imageExists==False:
            self.image_name = available_images[0]
        imageExists = False
        available_flavors = self.novaobj.flavors.list()
        for index in range(1,len(available_flavors)+1):
            if repr(available_flavors[index-1].name.lower()).find(self.flavor) != -1:
                self.flavor = available_flavors[index-1]
                imageExists = True
                break
        if imageExists==False:
            self.flavor = available_flavors[0]
        instance_name = os.environ['USER']+'-instance'
        name_index=0
        for eachname in self.novaobj.servers.list():
            name_index+=1
        instance_name = instance_name+(str(name_index+1))
        # Creating the instance
        self.instance = self.novaobj.servers.create(name=instance_name,image=self.image_name,flavor=self.flavor, key_name=keyname)

        # Checking the instance
        self.isActive()

    def createRules(self):
        isSshRulePresent = False
        isIcmpRulePresent = False
        for eachsecgrp in self.novaobj.security_groups.list():
            for eachrule in eachsecgrp.rules:
                if eachrule['ip_protocol'] == 'tcp' and eachrule['to_port'] == 22 and eachrule['from_port'] == 22:
                    isSshRulePresent = True
                if eachrule['ip_protocol'] == 'icmp' and eachrule['to_port'] == -1 and eachrule['from_port'] == -1:
                    isIcmpRulePresent = True

        if isSshRulePresent == False:
            self.novaobj.security_group_rules.create(self.novaobj.security_groups.find(name='default').id, ip_protocol='tcp', from_port=22, to_port=22)

        if isIcmpRulePresent == False:
            self.novaobj.security_group_rules.create(self.novaobj.security_groups.find(name='default').id, ip_protocol='icmp', from_port=-1, to_port=-1)

    def fetchIp(self,conf):
        self.createRules()
        isFloatingIpAssociated = False
        addresses = self.instance.addresses
        for eachpool in addresses.keys():
            for eachaddress in addresses[eachpool]:
                print eachaddress
                if eachaddress.has_key('OS-EXT-IPS:type'):
                    if eachaddress['OS-EXT-IPS:type'] == 'floating':
                        print 'Already has associated floating ip!'
                        isFloatingIpAssociated = True
                        self.ip = eachaddress['addr']
        if isFloatingIpAssociated == False:
            floatingip = self.novaobj.floating_ips.create(pool=conf.get('FLOATING_IP_POOL'))
            print floatingip,type(floatingip)
            self.instance = self.novaobj.servers.get(self.instance.id)
            self.instance.add_floating_ip(floatingip)
            self.ip = floatingip.to_dict()['ip']
    
    def getIp(self):
        return self.ip

    def getConnection(self):
        print 'Attempting connection to',self.ip
        return SshConnection(self.ip,"ubuntu",useKey=True)

    def isActive(self):
        self.instance = self.novaobj.servers.get(self.instance.id)
        status = self.instance.status
        while status == 'BUILD':
            print 'Current VM Status : ',status
            time.sleep(5)
            self.instance = self.novaobj.servers.get(self.instance.id)
            status = self.instance.status

        if (status != 'ACTIVE'):
            print 'VM Status : ',status
            return False

        print 'VM is ACTIVE'
        return True

if __name__=='__main__':
    conf = Configuration("openstackconfigs.conf")
    instanceObj = openStackInstance(conf)
    instanceObj.fetchIp(conf)
    #somehow ssh connection fails without this sleep. Probably because VM is still getting ready
    time.sleep(120)
    connectionObj = instanceObj.getConnection()
    connectionObj.run("pwd")
