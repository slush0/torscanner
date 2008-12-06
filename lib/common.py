import os
import hashlib
import ConfigParser
import threading

def log(text, level='INFO'):
    if level == 'INFO':
        print('>>> %s' % text)
    elif level == 'ERROR':
        #print '\033[0;1m!!! Error: %s\033[m' % text
        print('!!! Error: %s' % text)
    elif level == 'CMD':
        print('### %s' % text)
    else:
        print(text)

def hash(text = None):
    return hashlib.sha256(text)

def string2list(comma_string, separator=','):
    return map(lambda x: x.strip(), \
           comma_string.split(separator))
    
def uniqList(seq): 
    noDupes = []
    seq.sort()
    [noDupes.append(i) for i in seq if not noDupes.count(i)]
    return noDupes

# Merge config input from command line (higher priority) and config file.
# Returns a dict with final configuration set.
def mergeOptions(config, options):
    out = {}
    log('Using config directives:', 'INFO')
    for i,x in config.items('global'):
        try:
            v = eval('options.%s'%i)
            if v != None: out[i] = v
            else: out[i] = x
        except AttributeError:
            out[i] = x
        log('\t%s: %s' % (i, out[i]), 'INFO') 
    return out
    
def parseConfig(cfgs, defaults):
    config = ConfigParser.SafeConfigParser(defaults)
    for cfg in cfgs:
        cfg = os.path.abspath(os.path.expanduser(cfg))
        if os.path.exists(cfg):
            log("Using config file\t '%s'." % cfg)
            try:
                config.read(cfg)
            except Exception, e:
                log(e, 'ERROR')
                log("Config file corrupted, using built-in defaults.")
            break
    return config
    
def selectDatadir(datadirs):
    for ddir in datadirs:
        ddir = os.path.abspath(os.path.expanduser(ddir))
        if os.path.exists(ddir) and os.path.os.access(ddir, os.W_OK):
            log("Using data directory '%s'." % ddir)
            return ddir
    raise Exception, 'No datadir with writing access available!'

def loadPlugins(plugins):
    ret = {} # Loaded plugin objects
    for plugin in plugins:
        if plugin == '': continue
        log("Loading plugin '%s'..." % plugin)
        try:
            fp, pathname, description = imp.find_module(plugin)
            module = imp.load_module(plugin, fp, pathname, description)
            plg = module.Plugin()     
            
            # Check missing definitions in plugin (rules etc)
            try:
                plg._checkPlugin()
            except Exception, e:
                log("Plugin '%s' failed. Reason: %s" % (plugin, e), 'ERROR')
            else:
                # Everything looks OK
                ret[plugin] = plg
            
        except ImportError, e:
            log("Plugin '%s' failed. Reason: %s" % (plugin, e), 'ERROR')
    return ret
     
class counterClass(object):
    _dict = {}
   
    def __setattr__(self, name, value):
        self._dict[name] = value
        
    def __getattr__(self, name):
        return self._dict[name]
