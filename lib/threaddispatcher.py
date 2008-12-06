import hashlib
import common
import threading
import time
import sockctl

class threadWorker(threading.Thread):
    def __init__(self, threaddisp, opt, threadid):
        self.threaddisp = threaddisp
        self.threadid = threadid
        self.opt = opt
        self._stop = False
        self.timestamp = time.time()
        threading.Thread.__init__(self)
        self.DEBUG = True
        
    def updateTimestamp(self):
        self.timestamp = time.time()
        
    def stop(self):
        self._stop = True
        # FIXME: Must finalize current job!
                  
    def dlog(self, msg):
        if not self.DEBUG: return
        common.log("thread #%d, timestamp %f, %s" % (self.threadid, time.time(), msg), 'INFO')
        
    def run(self):
        common.log('Thread %d started'%self.threadid)
        
                
        while not self._stop:

            # pokud cas okruhu vetsi nez Dirtiness nebo zadny okruh, vytvor novy okruh
            # vyber url, ktere nebylo na danem okruhu testovano a ma failcount < maxfails
            # pokud neni url, vytvor novy okruh
            # pockej na vytvoreni okruhu (jojo, zamek)
            # pokud okruh nevytvoren, pridej failcount pro url.
            # stahni fajl
            # Uloz soubor do logu aktualniho exit node
            # Oznac kombinaci exit node a soubor za vyrizenou
            #

            self.dlog("Connecting to proxy")
            proxy = sockctl.Proxy('localhost', 9050)
            
            self.dlog("Connecting to final destination")            
            proxy.connect('slush.cz', 80)
            
            self.dlog("Sending request to final destination")
            proxy.send("GET /tortest.php HTTP/1.1\r\nHost: slush.cz\r\n\r\n")
            
            self.dlog("Waiting for data")
            data = proxy.recv()
            
            self.dlog("Data received, close connection")
            proxy.close()             
            
            self.updateTimestamp()
            #print "thread #%d, data: %s" % (self.threadid, data[0:10])
            print "thread #%d, timestamp %f, size %d" % (self.threadid, self.timestamp, len(data))
        
        print "Stopping #%d" % self.threadid
        
class threadDispatcher:
    
    def __init__(self, opt):
        self.opt = opt
        self.counter = common.counterClass()
        self.counter.threadid = 0
        self.threads = [] 
        self.maxthreads = int(opt['concurrentthreads'])
        self.maxtimeout = int(self.opt['threadtimeout'])
            
    def startThread(self):
        if len(self.threads) >= self.maxthreads:
            common.log("Maximum count of threads reached.", 'ERROR')
            return False

        t = threadWorker(self, self.opt, self.counter.threadid)
        try:
            t.start()
        except Exception, e:
            self.maxthreads = len(self.threads)
            common.log('startThread(): #%d, %s' %\
                (self.counter.threadid, e), 'ERROR')
            common.log('Updating ConcurrentThreads to '\
                       'value %d' % self.maxthreads, 'INFO')
            return False

        self.threads.append(t)            
        self.counter.threadid += 1
    
    def checkThreads(self):
        # Get actual timestamp
        tm = time.time()
        
        for t in self.threads:
            if self.maxtimeout and t.isAlive() and t.timestamp < (tm - self.maxtimeout):
                common.log("Thread #%d not responding. Let's stop it!" % t.threadid, 'INFO')
                
                common.log('checkThreads(): FIXME', 'ERROR')
                t.stop() # Must do some finalize of actual job
                
                del self.threads[self.threads.index(t)]
        
        if len(self.threads) < self.maxthreads:
            self.startThread()
