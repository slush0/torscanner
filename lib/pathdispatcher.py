import common
import random
import TorCtl

# These methods are called by thread running in scape of Tor controller (TorCtl.py).
# Don't forget to locks when accessing external objects!
class eventHandler(TorCtl.EventHandler):
    def circ_status_event(self, event):
        print event.circ_id
        print event.status
        print event.path
        print '----'
        
    def stream_status_event(self, event):      
        print event.event_name
        print event.arrived_at
        print event.strm_id
        print event.status
        print event.circ_id
        print event.target_host
        print event.target_port
        print event.reason
        print event.remote_reason
        print event.source
        print event.source_addr
        print '===================='
    
    def or_conn_status_event(self, orconn_event):
        print 'Connection status event:', orconn_event

    def new_desc_event(self, newdesc_event):
        print 'New descriptor event:', newdesc_event

class routerClass(TorCtl.Router):
    pass

class pathClass:
    def __init__(self, exitRouter, relayRouters):
        exitRouter.__class__ = routerClass
        self.exit = exitRouter
        self.idhex = self.exit.idhex
        self.nickname = self.exit.nickname
        self.relays = relayRouters

        #common.log('New path created: %s %s' % (self.nickname, self.idhex), 'INFO')
        
class pathDispatcher:
    def __init__(self, opt, controller):
        self.opt = opt
        self.ctl = controller
        self.paths = {}
        
        self.ctl.setEventHandler(eventHandler())
        self.network_status = self.ctl.ctl.get_network_status()
        
        common.log('Setting up Tor configuration...', 'INFO')
        self.ctl.ctl.set_option('MaxCircuitDirtiness', str(self.opt['maxcircuitdirtiness']))
        self.ctl.ctl.set_option('__LeaveStreamsUnattached','1')
        
        common.log('Reading router table...', 'INFO')
        self.routers = self.ctl.ctl.read_routers(self.network_status)
        
        self.relays, self.exits = self._filterRouters(self.routers)
        self._updatePaths()
        common.log('Exit nodes in database: %d' % len(self.paths), 'INFO')

    def _updatePaths(self):
        for e in self.exits:
            
            # Dont touch paths to known exit routers
            if e.idhex in self.paths: continue
            
            # For current exit node, select three random relays (without repeats!)
            route = []
            rels = self.relays[:] # Copy of original set of relays
            for i in range(int(self.opt['pathlength'])):
                rel = random.choice(rels)
                rels.remove(rel)
                route.append(rel)
                
            # Create new Path object
            self.paths[e.idhex] = pathClass(e, route)
        
    def _filterRouters(self, routers):
        exitflags = common.string2list(self.opt['exitflags']) 
        relayflags = common.string2list(self.opt['relayflags'])
        relayuptime = int(self.opt['relayuptime'])

        exits = []
        relays = []
        for i in routers:
            if not (False in (f in i.flags for f in exitflags)):
                exits.append(i)
                continue
            
            if not (False in (f in i.flags for f in relayflags)) \
                and i.uptime > relayuptime:
                relays.append(i)

        return (relays, exits)
'''    
class _router(object):
    def __init__(self, name):
        self.url = url
    
# Helper class as thread-safe counter     
class routerClass(object):
    _dict = {}
    lock = threading.Lock()
    
    def __setattr__(self, name, value):
        self.lock.acquire()
        self._dict[name] = value
        self.lock.release()
        
    def __getattr__(self, name):
        return self._dict[name]
       
class pathDispatcher:
    
    def __init__(self, opt):
        self.opt = opt
        self.urls = {}
        self.counter = counterClass()
        self.counter.todo = 0
        self.counter.done = 0
        self.counter.work = 0

    def submit(self, url):
        u = _url(url, urldisp=self)
        if u.url in self.urls:
            common.log('URL "%s" already exists in list' % u.url)
            # It doesnt fail, because it is currently working on URL
            return True

        if (self.counter.todo + self.counter.work) > int(self.opt['maxurls']):
            common.log('URL queue is full. Wait a moment and try again.')
            return False
        
        self.urls[u.url] = u
        self.counter.todo += 1
        
        common.log('URL "%s" added to list' % u.url, 'INFO')
        return True
    
    # Get instance of Url class from url queue for specified url
    def get(self, url):
        if url in self.urls:
            return self.urls[url]
        return None    
        
    # Select one URL and mark it as STATUS_WORK
    def getOne(self, markAsWork = True):
        for url in self.urls:
            u = self.urls[url]
            if u.status == STATUS_TODO:
                if markAsWork:
                    u.lock.acquire()
                    u.status = STATUS_WORK
                    u.lock.release()
                    self.counter.todo -= 1
                    self.counter.work += 1
                return u

        return None

    # Set URL as STATUS_DONE and move counters
    def setDone(self, url):
        self.urls[url].lock.acquire()
        self.urls[url].status = STATUS_DONE
        self.urls[url].lock.release()
        
        self.counter.work -= 1
        self.counter.done += 1

    def allDone(self):
        return self.counter.done > 0 and \
               self.counter.todo == 0 and \
               self.counter.work == 0
'''