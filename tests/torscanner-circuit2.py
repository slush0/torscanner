import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib-ext'))

from TorCtl import *
import TorUtil
import GeoIPSupport
import socks
import socket
import time
import random
import threading

TorUtil.loglevel = 'WARN'

class EventHandler(EventHandler):
    def circ_status_event(self, event):
        print event.circ_id
        print event.status
        print event.path
        print '----'
        global circ_ready
        global circ
        if event.circ_id == circ and event.status in ['BUILT']:
            circ_ready = True
        
    def stream_status_event(self, event):
        #TorCtl.DebugEventHandler.stream_status_event(self, event)
        global stream_id
        global circ
        global ctl
        #global stream_ready

        print event.event_name
        print event.arrived_at
        print event.strm_id
        print event.status
        print event.circ_id
        #global('circ)
        print event.target_host
        print event.target_port
        print event.reason
        print event.remote_reason
        print event.source
        print event.source_addr
        
        print 'stream_id', stream_id
        print 'circ', circ
        
        if event.strm_id == stream_id and event.status == 'SUCCEEDED' and event.circ_id != circ:
            print "FUUUUUUUUUUUUUUUUUUUUUUCK!!!!!!!!!!!!!!!!!!"
            print "FUUUUUUUUUUUUUUUUUUUUUUCK!!!!!!!!!!!!!!!!!!"
            
        if not stream_id and event.status in ['NEW']:
            stream_id = event.strm_id
            print "Stream %d created" % stream_id
            if event.circ_id != circ:
                print "Stream is ready to reattach by thread"
                ctl.ctl.attach_stream(stream_id, circ)
            
            #print "attach stream"   
            #print "StreamID %d, circid %d" % (stream_id, circ6)
            #print ctl.ctl.attach_stream(stream_id, circ)
        #if event.status == 'SENTCONNECT':
         
            #
        '''
        print event.event_name
        print event.arrived_at
        print event.strm_id
        print event.status
        print event.circ_id
        #global('circ)
        print event.target_host
        print event.target_port
        print event.reason
        print event.remote_reason
        print event.source
        print event.source_addr
        '''
        print '===================='
    
    def or_conn_status_event(self, orconn_event):
        print orconn_event

    def new_desc_event(self, newdesc_event):
        print newdesc_event
        
class Controller:
    '''Supporting class for talking with Tor Controller'''

    def __init__(self, host, port, pwd):
        '''Create connection to Tor controller'''
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host,port))
        self.socket = soc
        
        ctl = Connection(self.socket)
        ctl.authenticate(pwd)
        self.ctl = ctl
    
    def setEventHandler(self, eventHandler):
        self.ctl.set_event_handler(eventHandler)
        
    def addEvent(self, eventList = []):
        self.ctl.set_events(eventList, True) # Extending existing list
        
    def getSocksProxy(self):
        '''Return number of port, where Tor is listening as Socks proxy'''
        return int(self.ctl.get_option(["socksport"])[0][1])
    
class Proxy:
    '''Supporting class for talking with Tor Proxy'''

    def __init__(self, host, port):
        '''Create connection to Tor proxy'''
        self.proxyhost = host
        self.proxyport = port
        self.proxy = socks.socksocket()
        self.proxy.setproxy(socks.PROXY_TYPE_SOCKS5, self.proxyhost, self.proxyport)
        self.events = None
        
    def setEventHandler(self, eventHandler):
        self.events = eventHandler
        
    def connect(self, host, port):
        '''Create connection to target site thru Tor proxy'''
        self.host = host
        self.port = port
        self.proxy.connect((host, port))

    def close(self):
        self.proxy.close()
        
    def send(self, data):
        self.proxy.sendall(data)
        
    def recv(self):
        data = ''
        read = self.proxy.recv(4096)
        while read:
                data += read
                print read
                read = self.proxy.recv(4096)
        return data

class RouterManagement:
    def __init__(self, controller):
        self.ctl = controller
        self.network_status = self.ctl.ctl.get_network_status()
        self.routers = self.ctl.ctl.read_routers(self.network_status)
        
        self.relays, self.exits = self._filterRouters(self.routers)

    def _filterRouters(self, routers):
        exitflags = ['Exit', 'Running', 'Valid']
        relayflags = ['Running', 'Valid', 'Fast']
        relay_uptime = 86400
        
        exits = []
        relays = []
        for i in routers:
            '''print i.idhex
                print i.nickname
                print i.exitpolicy
                print i.flags
                print i.down'''
            if not (False in (f in i.flags for f in exitflags)):
                exits.append(i)
                    
            if 'Exit' not in i.flags and \
                not (False in (f in i.flags for f in relayflags)) \
                and i.uptime > relay_uptime:
                relays.append(i)

        return (relays, exits)

class threadWorker(threading.Thread):
    def run(self):
        global ctl
        global stream_id
        global circ
        global circ_ready
        
        done = False
        while(1):
            print stream_id, circ, circ_ready
            if not done and circ_ready and stream_id:
                ctl.ctl.attach_stream(stream_id, circ)
                done = True
                print "Thread finishing"
            time.sleep(1)
        
    #def walkCircuits
torhost = 'localhost'
torproxyport = 9050
torctlport = 9051
torctlpass = ''

events = EventHandler()

stream_id = 0
circ = 0
circ_ready = False

ctl = Controller(torhost, torctlport, torctlpass)
ctl.setEventHandler(events)
ctl.addEvent(['STREAM', 'CIRC', 'ORCONN', 'NEWDESC'])

thrd = threadWorker()
#thrd.start()
'''
Solution (for others):

1) Create circuit (main thread)
2) Call socket.connect() (main thread)
3) call ctl.attach_stream() from Tor callback handler (it is separate thread) instead of waiting on stream_id in main thread.
4) Then, socket.connect() will return socket in main thread
'''
#rmgmt = RouterManagement(ctl)

#output = open('data.pkl', 'rb')
#sorted_rlist = pickle.load(output)
#output.close()


#print "Routers ----------------------"
#print [r.nickname for r in routers]
#print "Exit nodes -------------------"        
#print [r.nickname for r in exits]

# !!!!!!!!!!!!!!!!!!!!!!!!!!!


'''
i = 0
for e in rmgmt.exits:
    if e.will_exit_to('255.255.255.255', 80):
        rand = random.randint(0, len(rmgmt.routers)-1)
        router = rmgmt.routers[rand]
        print "%s (%s), %s (%s)" % (router.nickname, router.idhex, e.nickname, e.idhex)
        ccid = ctl.ctl.extend_circuit(0,[rmgmt.routers[rand].idhex, e.idhex])
        print "New circuit #%d" % ccid
        time.sleep(2)
        i += 1
    if i > 2: break
'''
        
#for c in country.iterkeys():
#    print "%s -------------" % c
#    for e in country[c]:
#        if e.will_exit_to('84.42.190.108', 80):
#            rand = random.randint(0, len(routers)-1)
#            print "%d, %d" % (len(routers), rand)
#            print "%s, %s" % (routers[rand].nickname, e.nickname)

#ctl.ctl.set_option('__LeaveStreamsUnattached','0')


circ = ctl.ctl.extend_circuit(0,["moria1", 'podgornycz'])
ctl.ctl.extend_circuit(0,["moria1", 'mwserver'])

print "circ id", circ

while(not circ_ready):
    time.sleep(1)
    print "Circ ready", circ_ready
print "Circ ready", circ_ready

print "Connecting to proxy"
proxy = Proxy(torhost,torproxyport)
#proxy.setEventHandler(events)

print "connecting to destination"
proxy.connect('slush.cz', 80)

while(not stream_id):
    time.sleep(1)
    print "Stream id", stream_id
print "Stream id", stream_id

#ctl.ctl.attach_stream(stream_id, circ)
print "Downloading file"
proxy.send("GET /tortest.php HTTP/1.1\r\nHost: slush.cz\r\n\r\n")
print "recv"
proxy.recv()
print "close"
proxy.close()
print "exit"
sys.exit()
#ctl.ctl.close_circuit(circ)
#ctl.ctl.close_circuit(circ)
#print "Exit by pressing Ctrl+C"
#for i in range(10):
#    time.sleep(1)
