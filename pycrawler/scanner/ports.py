import socket
import time
# Very crud port scanner class
class PortScanner():

    MAX_RANGE=65536

    def __init__(self,server,ports={},delay=0.01,timeout=0.1):
        self.serverip=server
        self.knownports=ports
        self.delay=delay
        self.timeout=timeout

    def scan(self):
        ports = []
        k = self.knownports.keys()
        try:
            for port in k:
                time.sleep(self.delay)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.serverip, int(port)))
                if result == 0:
                    print "Ip: {}, Port {}: 	 Open".format(self.serverip,port)
                    ports.append({port:self.knownports[port]})
                else:
                    print "Ip: {}, Port {}: 	 Closed".format(self.serverip,port)
                sock.close()
        except socket.error:
            print "Couldn't connect to server"
            return []
        return ports
