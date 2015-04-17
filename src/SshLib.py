import paramiko
import os

class SshConnection(object):
	ssh = paramiko.client.SSHClient()

	def __init__(self,host,user,password=None,useKey=False):
		self.host=host
		self.user = user
		self.password = password
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		if useKey==False:
			self.ssh.connect(host,username=self.user,password=self.password)
		else:
			self.ssh.connect(host,username=self.user,key_filename=os.environ['HOME']+"/.ssh/id_rsa")

	def run_old(self,command,password=None):
		channel = self.ssh.get_transport().open_session()
		if password==None:
			get_pty=False
		else:
			get_pty=True
		print "starting command"
		stdin,stdout,stderr = self.ssh.exec_command(command,get_pty=get_pty)
		if password!=None:
			stdin.write(password+"\n")
			stdin.flush()
		stdin.close()
		#print type(stdout)
		for line in stdout.readlines():
			print line.strip()
		for line in stderr.readlines():
			print line.strip()
		#exit_code =channel.recv_exit_status()
		#print"Exit Code=",exit_code
		#if exit_code!=0:
		#	exit()

	def run(self,command,password=None):
		#channel = self.ssh.get_transport().open_session()
		if password==None:
			get_pty=False
		else:
			get_pty=True
		print "Running command on "+self.host+": "+command
		stdin,stdout,stderr = self.ssh.exec_command(command,get_pty=get_pty)
		if password!=None:
			stdin.write(password+"\n")
			stdin.flush()
		stdin.close()
		for line in stdout:
			print line.strip()
		for line in stderr:
			print line.strip()
		exit_code =stdout.channel.recv_exit_status() 
		return exit_code
		#if exit_code!=0:
		#	exit()

	def run_shell(self,command,password=None):
		channel=self.ssh.invoke_shell()
		if password==None:
			get_pty=False
		else:
			get_pty=True
		print "Running command: "+command
		stdin,stdout,stderr = channel.exec_command(command)
		if password!=None:
			stdin.write(password+"\n")
			stdin.flush()
		stdin.close()
		for line in stdout:
			print line.strip()
		for line in stderr:
			print line.strip()
		exit_code =stdout.channel.recv_exit_status() 
		return exit_code
		#if exit_code!=0:
		#	exit()

	def close(self):
		self.ssh.close()