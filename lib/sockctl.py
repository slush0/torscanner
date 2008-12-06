import TorCtl
import GeoIPSupport
import socks
import socket

class evHandler(TorCtl.EventHandler):
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
        
class Controller:
    '''Supporting class for talking with Tor Controller'''
    
    def __init__(self, host, port, pwd):
        '''Create connection to Tor controller'''
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((host,port))
        self.socket = soc
        
        ctl = TorCtl.Connection(self.socket)
        ctl.authenticate(pwd)
        self.ctl = ctl
        self.setEventHandler(evHandler())
    
    def setEventHandler(self, eventHandler):
        self.ctl.set_event_handler(eventHandler)
        
    def addEvent(self, eventList = []):
        self.ctl.set_events(eventList, True) # Extending existing list
    
    def getSocksPort(self):
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
        read = self.proxy.recv(512)
        while read:
                data += read
                #print read
                read = self.proxy.recv(512)
        return data
'''
class RouterManagement:
    def __init__(self, controller):
        self.ctl = controller
        self.network_status = self.ctl.ctl.get_network_status()
        self.routers = self.ctl.ctl.read_routers(self.network_status)
        
        self.relays, self.exits = self._filterRouters(self.routers)

    def _filterRouters(self, routers):
        exitflags = ['Exit', 'Running', 'Valid']
        relayflags = ['Running', 'Valid', 'Fast']
        relayuptime = 86400
        
        exits = []
        relays = []
        for i in routers:
            if not (False in (f in i.flags for f in exitflags)):
                exits.append(i)
                    
            if 'Exit' not in i.flags and \
                not (False in (f in i.flags for f in relayflags)) \
                and i.uptime > relayuptime:
                relays.append(i)

        return (relays, exits)
'''
