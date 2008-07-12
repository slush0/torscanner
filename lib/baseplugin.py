class BasePlugin():
    def __init__(self):
        self.name = ''
        self.init()
        
    def init(self):
        raise ImportError, 'You have to override init() function!'
    
    def _checkPlugin(self):
        if self.name == '': raise Exception, 'Plugin name not defined'
        if not len(self.getRules()): raise Exception, 'Rules not defined'
        
    def defRule(self, protocol, fileType, contentType):
        return {'protocol': protocol,
                'filetype': fileType,
                'contenttype': contentType}
    
    def getRules(self):
        return []
        