import optparse
import ConfigParser
import imp
import os

def log(text, level='INFO'):
    if level == 'INFO':
        print '>>> %s' % text
    elif level == 'ERROR':
        #print '\033[0;1m!!! Error: %s\033[m' % text
        print '!!! Error: %s' % text
    elif level == 'CMD':
        print '### %s' % text
    else:
        print text
        
def parseOptions():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    
    parser.add_option("-c", "--config", dest='config',
                      metavar="FILE", help="I will use specific config file"),
    parser.add_option("-d", "--data", dest='data',
                      metavar="FILE", help="I will use specific data directory"),
    parser.add_option("--no-prep", action="store_false",
                      dest="preparation", default=True,
                      help="Don't run first phase (web spider). I will take last "\
                      "used bucket of links")
    parser.add_option("--no-exec", action="store_false",
                      dest="execution", default=True,
                      help="Don't run second phase (execution). I won't test "\
                      "any Exit node")
    parser.add_option("--no-analyse", action="store_false",
                      dest="analysis", default=True,
                      help="Don't run third phase (analysis). I will skip "\
                      "gathering data from second phase.")

    return parser.parse_args()

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