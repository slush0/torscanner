import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib-ext'))

from TorCtl import *
import socks
import socket
import time

#def test(event):
        #TorCtl.DebugEventHandler.stream_status_event(self, event)
#        print event.strm_id
        
stream_id = 0
circ_ready = False
circ6 = None

class EventHandler(DebugEventHandler):
    def circ_status_event(self, event):
        print event.circ_id
        print event.status
        print event.path
        print '----'
        global circ_ready
        global circ6
        if event.circ_id == circ6 and event.status == 'BUILT':
            circ_ready = True
        
    def stream_status_event(self, event):
        #TorCtl.DebugEventHandler.stream_status_event(self, event)
        global stream_id
        global circ6
        global stream_ready

        if event.status == 'NEW':
            stream_id = event.strm_id
            print "attach stream"   
            print "StreamID %d, circid %d" % (stream_id, circ6)
            print ctl.ctl.attach_stream(stream_id, circ6)
        #if event.status == 'SENTCONNECT':
         
            #
        
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
    
class Controller:
    '''Supporting class for talking with Tor Controller'''
    
    def __init__(self, host, port, pwd):
        '''Create connection to Tor controller'''
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host,port))
        self.socket = soc
        
        ctl = Connection(self.socket)
        print ctl
        ctl.authenticate(pwd)
        self.ctl = ctl
        #ctl.set_event_handler(TorCtl.DebugEventHandler())
        #ctl.set_event_handler(EventHandler())
        #ctl.set_events(['STREAM'])
        
        #ctl.launch_thread()
        #ctl.set_event_handler(stream_status_event)
    
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
                return data # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                read = self.proxy.recv(4096)
        return data
        
torhost = 'localhost'
torproxyport = 9050
torctlport = 9051
torctlpass = ''

events = EventHandler()
#events.stream_status_event = test

ctl = Controller(torhost, torctlport, torctlpass)
ctl.setEventHandler(events)
ctl.addEvent(['STREAM', 'CIRC'])
#for i in range(300):
circ1 = ctl.ctl.extend_circuit(0,["jalopy", 'crelm'])
circ6 = ctl.ctl.extend_circuit(0,["bmwanon", 'crelm'])
circ3 = ctl.ctl.extend_circuit(0,['tritlax2', 'crelm'])
circ4 = ctl.ctl.extend_circuit(0,['torxmission', 'crelm'])
        # Montesuma
    #circ5 = ctl.ctl.extend_circuit(0,["baphomet", 'mwserver', 'charlesbabbage'])
    #circ2 = ctl.ctl.extend_circuit(0,['mwserver', 'BostonUCompSci'])
#print "Waiting to circ %d" % circ6
while 1:
    time.sleep(1)
    print "Waiting to circuit"
    #f circ_ready == True:
    #   break
    
#
#ctl.ctl.attach_stream(stream_id, circ1)
#proxy = Proxy(torhost,torproxyport)
#proxy.setEventHandler(events)




#proxy.connect('releases.ubuntu.com', 80)

#proxy.send("GET /8.04.1/ubuntu-8.04.1-alternate-i386.iso HTTP/1.1\r\nHost: releases.ubuntu.com\r\n\r\n")
#proxy.recv()
#proxy.close()

#ctl.ctl.close_circuit(circ)
#ctl.ctl.close_circuit(circ)
print "Exit by pressing Ctrl+C"
for i in range(10):
    time.sleep(1)
