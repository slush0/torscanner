import common
import threading
import SimpleXMLRPCServer

class RPCServer(threading.Thread):
    #import common
    quit = False

    class XMLRPCInterface:
        def submit_url(self, url):
            return self.urldisp.submit(url)
        
        def get_url_status(self, url):
            return self.urldisp.get(url).progress()
        
        def get_scanner_status(self):
            return True
        
        def quit(self):
            self.server.shutdown()
            return True
    
    def shutdown(self):
        self.quit = True

    def run(self):
        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer(
                        (self.opt['serverhost'], int(self.opt['serverport'])))
        #common.log('XML-RPC server is not running...', 'INFO')
            
        self.server.register_introspection_functions()
        iface = self.XMLRPCInterface()
        iface.urldisp = self.urldisp
        iface.server = self
        self.server.register_instance(iface)
        common.log('XML-RPC server started succesfully...', 'INFO')
        
        # Run the server's main loop    
        while not self.quit:
            self.server.handle_request()

        common.log('XML-RPC server thread shutdown', 'INFO')
