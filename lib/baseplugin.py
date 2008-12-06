'''
Base class for Protocol plugins. All Protocol plugins should use this
class as its parent.

call flow:
    __init__()
        getRules()
            defRule()
            defRule() ...
    _checkPlugin()
    checkLink()
    checkLink() ...
    
    _analyze()
        probe()
        analyze()
'''

class Link():
    def __init__(self, url, headers = {}, protocol = ''):
        self.protocol = protocol
        self.url = url
        self.headers = headers
        self.port = 0
        self.host = ''
        self.path = ''
        print "Link init: TODO"
        
class BasePlugin():
    def __init__(self):
        self.name = ''
        self.init()
        self.rules = self.getRules()
    
    def _checkPlugin(self):
        if self.name == '': raise Exception, 'Plugin name not defined'
        if not len(self.rules): raise Exception, 'Rules not defined'
        if type(self.rules) != type([]): raise Exception, 'getRules() result have to be list of Link()'

        linkclass = Link('').__class__
        for r in self.rules:
            if r.__class__ != linkclass:
                raise Exception, 'Rules are not derived from Link class'
        self.checkLink(Link(''))

    # TODO: Call TorCtl method to checking exit policy of node
    def _checkExitPolicy(self, host, port):
        return True
    
    # Override this in your custom plugin.
    def init(self):
        self.name = 'Blank plugin'
        raise ImportError, 'You have to override init() function!'

    # Phase 2
    def _analyze(self, socket, link):
        content = self.probe(socket, link)
        self.analyze(link, content)
   
    # Phase 1
    # Check, if spider found file interesting for this plugin.
    # Return True, if file should be tested thru exit nodes.
    # Override this in your custom plugin.
    def checkLink(self, link):
        raise ImportError, 'You have to override checkLink() function!'
        return True

    # Phase 2
    # Should obtain link using specified socket connection.
    # In case of HTTP protocol, it simply download file 'link' thru 'socket'.
    # Dont forget to call '_checkExitPolicy'
    def probe(self, socket, link):
        raise ImportError, 'You have to override probe() function!'
    
    # Phase 2
    # 'content' is output of probe function. Should anaylze given data
    # and return tree of hashes (see spec)
    def analyze(self, link, content = None):
        raise ImportError, 'You have to override analyze() function!'

    # Should return list of defRules().
    # Each file found by web spider will be compared against
    # these rules. If file pass the test, will be added to list
    # of files for testing exit nodes.
    # Override this in your custom plugin.
    def getRules(self):
        raise ImportError, 'You have to override getRules() function!'
        return []
        