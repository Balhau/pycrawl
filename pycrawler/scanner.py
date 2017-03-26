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

dict_ports={
	"1" 	: 	"TCPMUX",
	"2" 	: 	"RMJOBENTRY",
	"7" 	: 	"ECHO",
	"9" 	: 	"DISCARD",
	"11"	: 	"SYSTAT",
	"13"	: 	"DAYTIME",
	"17"	: 	"QOTD",
	"18"	: 	"MSP",
	"19"	:	"CHARGEN",
	"20"	:	"FTP",
	"21"	:	"FTP",
	"22"	:	"SSH",
	"23"	:	"TELNET",
	"25"	:	"SMTP",
	"37"	:	"TIME",
	"39"	:	"RAP",
	"42"	:	"HNS",
	"43"	:	"WHOIS",
	"49"	:	"TACACS",
	"50"	:	"RMCP",
	"53"	:	"DNS",
	"67"	:	"BOOTP_S",
	"68"	:	"BOOTP_C",
	"69"	:	"TFTP",
	"70"	:	"GOPHER",
	"71"	:	"NETRJS",
	"72"	:	"NETRJS",
	"73"	:	"NETRJS",
	"79"	:	"FINGER",
	"80"	:	"HTTP",
	"88"	:	"KERBEROS",
	"101"	:	"NIC",
	"102"	:	"TSAP",
	"104"	:	"DICOM",
	"105"	:	"CCSO",
	"107"	:	"RUTS",
	"109"	:	"POP2",
	"110"	:	"POP3",
	"111"	:	"ONC_RPC",
	"113"	:	"IRC_IDENT",
	"115"	:	"SFTP",
	"117"	:	"UUCP",
	"118"	:	"SQLP",
	"119"	:	"NNTP",
	"123"	:	"NTP",
	"135"	:	"EPMAP",
	"137"	:	"NETBIOS",
	"139"	:	"NETBIOS",
	"143"	:	"IMAP",
	"161"	:	"SNMP",
	"170"	:	"PRINT",
	"177"	:	"XSERVER",
	"179"	:	"BGP",
	"194"	:	"IRC",
	"199"	:	"SNMP",
	"201"	:	"APPLE_TALK",
	"209"	:	"QMTP",
	"213"	:	"IPX",
	"220"	:	"IMAP",
	"259"	:	"ESRO",
	"389"	:	"LDAP",
	"399"	:	"DECNet",
	"401"	:	"UPS",
	"427"	:	"SLP",
	"434"	:	"MIP",
	"443"	:	"HTTPS",
	"444"	:	"SNPP",
	"445"	:	"SAMBA",
	"464"	:	"KERBEROS",
	"465"	:	"SMTPS",
	"512"	:	"REXEC",
	"513"	:	"RLOGIN",
	"514"	:	"RSHELL",
	"515"	:	"LPD",
	"520"	:	"EFS",
	"530"	:	"RPC",
	"546"	:	"DHCP6_CLIENT",
	"547"	:	"DHCP6_SERVER",
	"554"	:	"RTSP",
	"563"	:	"NNTPS",
	"585"	:	"IMAPS",
	"674"	:	"ACAP",
	"749"	:	"KERBEROS",
	"843"	:	"ADOBE_FLASH",
	"992"	:	"TELNETS",
	"993"	:	"IMAPS",
	"994"	:	"IRCS",
	"995"	:	"POP3S",
	"2181"	:	"ZOOKEEPER",
	"3128"	:	"HTTP_PROXY",
	"3306"	:	"MYSQL",
	"5000"	:	"HTTP",
	"5433"	:	"HTTPS",
	"6667"	:	"IRC",
	"6697"	:	"IRCS",
	"8000"  :	"HTTP",
	"8080"	:	"HTTP",
	"8081"	:	"HTTP",
	"9000"	:	"HTTP",
	"9090"	:	"HTTP",
	"9092"	:	"KAFKA",
	"9091"	:	"HTTP"
}

known_ports=[1,5,7,9,11,13,17,18,19,20,21,22,23,25,37,39,42,43,49,50,53,67,68,69,70,71,72,73,73,79,80,
88,101,102,104,105,107,109,110,111,113,115,117,119,123,137,138,139,143,161,162,163,164,174,177,178,179,191,
194,1,201,202,204,206,209,210,213,220,245,347,363,369,370,372,389,427,434,435,443,444,445,464,468,487,488,
496,500,535,538,546,547,554,563,565,587,610,611,612,631,636,674,694,749,750,765,767,873,992,993,994,995,
3128,3306,5433,5432,6667,6697,8080,8081,8000,9000,9090,9091]

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
			portscan = PortScanner(ip,ports=dict_ports,timeout=0.2)
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
