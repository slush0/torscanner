import sys
sys.path.append('lib')
import TorCtl       # https://www.torproject.org/svn/torflow/TorCtl/
import GeoIPSupport # -||-
import socks        # http://socksipy.sourceforge.net/

import ConfigParser
import socket
import time
import random
import pickle
import os
import time

stream_id = 0
circ_ready = False
circ = None

class EventHandler(TorCtl.DebugEventHandler):
    def circ_status_event(self, event):
        print event.circ_id
        print event.status
        print event.path
        print '----'
        global circ_ready
        global circ
        if event.circ_id == circ and event.status == 'BUILT':
            circ_ready = True
        
    def stream_status_event(self, event):
        TorCtl.DebugEventHandler.stream_status_event(self, event)
        global stream_id
        global circ
        global stream_ready

        if event.status == 'NEW':
            stream_id = event.strm_id
            print "attach stream"   
            print "StreamID %d, circid %d" % (stream_id, circ)
#            print ctl.ctl.attach_stream(stream_id, circ)
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
        
        ctl = TorCtl.Connection(self.socket)
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

nslist = ctl.ctl.get_network_status()
sorted_rlist = ctl.ctl.read_routers(nslist)

#output = open('data.pkl', 'rb')
#sorted_rlist = pickle.load(output)
#output.close()

output = open('data.pkl', 'wb')
pickle.dump(sorted_rlist, output)
output.close()

exits = []
routers = []
country = {}
for i in sorted_rlist:
    i = GeoIPSupport.GeoIPRouter(i)
    print i.nickname, i.contact        
    if 'Exit' in i.flags and 'Running' in i.flags and 'Valid' in i.flags:
        exits.append(i)
        try:
            country[i.country_code].append(i)
        except:
            country[i.country_code] = []
            country[i.country_code].append(i)
            
        '''print i.idhex
        print i.nickname
        print i.exitpolicy
        print i.flags
        print i.down
        print '-----'
        '''
    if 'Exit' not in i.flags and 'Running' in i.flags and \
        'Valid' in i.flags and i.uptime > 86400:
        routers.append(i)
        
for c in country.iterkeys():
    print "%s -------------" % c
    for e in country[c]:
        if e.will_exit_to('84.42.190.108', 80):
            rand = random.randint(0, len(routers)-1)
            print "%d, %d" % (len(routers), rand)
            print "%s, %s" % (routers[rand].nickname, e.nickname)
            
#print ctl.ctl.get_network_status()
#circ = ctl.ctl.extend_circuit(0,['mushin', 'tortila'])
#print "Waiting to circ %d" % circ
#while 1:
#    time.sleep(1)
#    print "Waiting to circuit"
#    if circ_ready == True:
#        break
    
#
#ctl.ctl.attach_stream(stream_id, circ)
#proxy = Proxy(torhost,torproxyport)
#proxy.setEventHandler(events)



'''
proxy.connect('releases.ubuntu.com', 80)

proxy.send("GET /8.04.1/ubuntu-8.04.1-alternate-i386.iso HTTP/1.1\r\nHost: releases.ubuntu.com\r\n\r\n")
proxy.recv()
proxy.close()

print "Exit by pressing Ctrl+C"
while 1:
    time.sleep(1)
'''