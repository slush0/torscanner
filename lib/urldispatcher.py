import hashlib
import common
import threading

STATUS_TODO = 1
STATUS_WORK = 2
STATUS_DONE = 3 

class _url(object):
    def __init__(self, url, urldisp = None):
        self.url = url
        self.hash = hashlib.sha256(url).hexdigest()
        self.status = STATUS_TODO 
        self.urldisp = urldisp
    
    def setDone(self):
        self.urldisp.setDone(self.url)
    
    # Return some info about current state of url
    def progress(self):
        return {'status': self.status}

class urlDispatcher:
        
    def __init__(self, opt):
        self.opt = opt
        self.urls = {}
        self.lock = threading.Lock()
        self.counter = common.counterClass()
        self.counter.todo = 0
        self.counter.done = 0
        self.counter.work = 0

    def submit(self, url):
        self.lock.acquire()
            
        if url in self.urls:
            common.log('URL "%s" already exists in list' % url)
            # It doesnt fail, because it is currently working on URL
            self.lock.release()
            return True
        
        if (self.counter.todo + self.counter.work) >= int(self.opt['maxurls']):
            common.log('URL queue is full. Wait a moment and try again.')
            self.lock.release()
            return False
        
        self.urls[url] = _url(url, urldisp=self)
        self.counter.todo += 1
        
        #common.log('URL "%s" added to list' % url, 'INFO')
        self.lock.release()
        return True
    
    # Get instance of Url class from url queue for specified url
    def get(self, url):
        if url in self.urls:
            return self.urls[url]
        return None    
        
    # Select one URL and mark it as STATUS_WORK
    def getOne(self, markAsWork = True):
        self.lock.acquire()
        ret = None
        for url in self.urls:
            u = self.urls[url]
            if u.status == STATUS_TODO:
                if markAsWork:
                    u.status = STATUS_WORK
                    self.counter.todo -= 1
                    self.counter.work += 1
                ret = u
                break

        self.lock.release()
        return ret

    # Set URL as STATUS_DONE and move counters
    def setDone(self, url):
        self.urls[url].status = STATUS_DONE       
        self.counter.work -= 1
        self.counter.done += 1

    def allDone(self):
        return self.counter.done > 0 and \
               self.counter.todo == 0 and \
               self.counter.work == 0