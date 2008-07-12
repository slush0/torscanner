import baseplugin
class Plugin(baseplugin.BasePlugin):
    def init(self):
        self.name = 'HTTP Plugin'

    def getRules(self):
        return [self.defRule('http', '.*', 'text\/html')]