from kazoo.client import KazooClient
import time
import uuid
import signal
import sys
import socket
import yaml
from scanner.ports import PortScanner
from portdict import *
from utils.ports import IpUtils
from kafka import KafkaProducer
import json

CONFIG_FILE = "config.yaml"
props = None

with open(CONFIG_FILE,'r') as f:
	props = yaml.load(f)

portscanntopic = props['kafka']['topics']['portscan']
zookeeper_path = props['zookeeper']['path']

print "Loaded props: %s" % props
print "Portscan kafka topic: %s" % portscanntopic

kp=KafkaProducer(bootstrap_servers=props['kafka']['hosts'])

class CrawlerCluster():
	def __init__(self,zk_root,children=None):
		self.zk_root=zk_root
		self.children = children
		self.zk = KazooClient(hosts=zookeeper_path)

	def watch_peers(self,children):
		#set another watch
		self.children = self.zk.get_children(self.zk_root, watch=self.watch_peers)


	def connectZookeeper(self):
		print "Registering to Cluster"
		host = socket.gethostname()
		self.zk.start()
		self.zk.ensure_path(self.zk_root+"/"+host)
		self.children = self.zk.get_children(self.zk_root, watch=self.watch_peers)
		self.uid = str(uuid.uuid1())
		self.zk.create(self.zk_root+"/"+host+"/"+self.uid,self.uid,ephemeral = True)


	def scanPorts(self):
		while(True):
			#print "Peers : %s" % len(self.children)
			ip = IpUtils.randomIPV4()
			print "Scanning: %s" % ip
			portscan = PortScanner(ip,ports=DICT_PORTS,timeout=0.2)
			ports = portscan.scan()
			message={}
			message['ip']=ip
			message['ports']=ports
			message['crawlerid']=self.uid
			message['crawlerhost']=socket.gethostname()
			msgstr=json.dumps(message)
			kp.send(props['kafka']['topics']['portscan'],msgstr,ip)
			print ports
			#print IpUtils.randomIPV4()

	def closeZookeeper(self):
		print "Closing zookeeper"
		self.zk.stop()
		self.zk.close()

	def printPeers(self):
		for p in self.children:
			print p

def main():
	cl = CrawlerCluster("/balhau/crawler")

	def exit_handler(signa,frame):
		print "Exiting. Disconnecting from zookeeper"
		cl.printPeers()
		cl.closeZookeeper()
		sys.exit(0)

	signal.signal(signal.SIGINT,exit_handler)

	cl.connectZookeeper()
	cl.scanPorts()
	cl.closeZookeeper()


if __name__ == '__main__':
	main()
