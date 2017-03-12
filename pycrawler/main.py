from kazoo.client import KazooClient
import time
import uuid
import signal
import sys
import socket
import yaml
from scanner.ports import PortScanner
from utils.ports import IpUtils
from kafka import KafkaProducer
import json

CONFIG_FILE = "config.yaml"
props = None

known_ports=[1,5,7,9,11,13,17,18,19,20,21,22,23,25,37,39,42,43,49,50,53,63,67,68,69,70,71,72,73,73,79,80,
88,95,101,102,105,107,109,110,111,113,115,117,119,123,137,138,139,143,161,162,163,164,174,177,178,179,191,
194,1,201,202,204,206,209,210,213,220,245,347,363,369,370,372,389,427,434,435,443,444,445,464,468,487,488,
496,500,535,538,546,547,554,563,565,587,610,611,612,631,636,674,694,749,750,765,767,873,992,993,994,995,
3128,5432,8080,8081,8000]

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
			time.sleep(1)
			#print "Peers : %s" % len(self.children)
			ip = IpUtils.randomIPV4()
			print "Scanning: %s" % ip
			portscan = PortScanner(ip,ports=known_ports,timeout=0.2)
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
