#!/usr/bin/python

'''
    Exit statuses:
        -1:    Module dependency error.
        0:     Program finished on unexpected point, but not on exception.
        1:     Program finished on unhandled exception. Please REPORT to author.
        42:    Program finished succesfully.
'''

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib-ext'))

try:
    # Specialities
    import TorCtl       # https://tor-svn.freehaven.net/svn/torctl/trunk/python/TorCtl/
    import GeoIPSupport # -||-
    import socks        # http://socksipy.sourceforge.net/
    import TorUtil

    # TorScanner modules
    import common
    import rpcserver
    import urldispatcher
    import threaddispatcher
    import pathdispatcher
    import sockctl

    # Standard Python modules
    import ConfigParser
    import socket
    import time
    import threading
    import time
    import optparse
    import SimpleXMLRPCServer
    import imp
    import hashlib
    import random
#    import pickle
    
except ImportError, e:
    print "%s, please install it and run again." % e
    sys.exit(-1)

# Will use first directory with "write" permission as data directory
DATADIR_PATHS = ['/var/lib/torscanner', '~/.torscanner', '.']
DATADIR_USER = '~/.torscanner'

# Config files with priorities. First file with higher priority.
CONFIG_PATHS = ['./torscanner.conf',               # Current directory
                '~/.torscanner/torscanner.conf', # User directory
                '/etc/torscanner.conf']          # System directory

# Use this settings when config file not found or any directive missing.
CONFIG_DEFAULTS = {
                   'TorCommand': '',
                   'TorHost': 'localhost',
                   'TorControlPort': 9051,
                   'TorControlPwd': '',
                   'EnableServer': 0,
                   'ServerHost': 'localhost',
                   'ServerPort': 8086,
                   'TorDebug': 'WARN',
                   'MaxCircuitDirtiness': 500,
                   'RelayUptime': 86400,
                   'RelayFlags': 'Running, Valid, Fast',
                   'ExitFlags': 'Exit, Running, Valid',
                   'PathLength': 3, 
                   'ConcurrentThreads': 10,
                   'MinUrls': 10,
                   'MaxUrls': 100                
                   }

def parseOptions():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    
    parser.add_option("-c", "--config", dest='config',
                      metavar="FILE", help="Use specific config file"),
    parser.add_option("-d", "--data", dest='data',
                      metavar="FILE", help="Use specific data directory"),
    parser.add_option("-s", "--source", dest='source',
                      metavar="FILE", help="Load URLs from source file"),                      
    parser.add_option("-r", "--dirtiness", dest='maxcircuitdirtiness',
                      help="How often rotate circuits (MaxCircuitDirtiness)")
    parser.add_option("-t", "--threads", dest='concurrentthreads',
                      help="How many concurrent threads use to scanning")
    parser.add_option("-u", "--urls", dest='minurls',
                      help="Minimum number of urls to vertical analysis of node")
    parser.add_option("-m", "--max-urls", dest='maxurls',
                      help="Maximum number of urls held in memory at the same time")

    return parser.parse_args()

if __name__ == '__main__':
    
    # Parsing command line arguments
    (options, args) = parseOptions()
    
    common.log('Starting TorScanner at %s UTC...' % \
               time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), 'CMD')
    
    #Joining cmdline param 'config' and list of default places
    cfgs = []
    if options.config: cfgs.extend([options.config])
    cfgs.extend(CONFIG_PATHS)

    # Loading configuration file
    config = common.parseConfig(cfgs, CONFIG_DEFAULTS)
        
    #Joining cmdline param 'data' and list of default datadir places
    datadirs = []
    if options.data: datadirs.extend([options.data])
    datadirs.extend(DATADIR_PATHS)

    # Selecting data directory. Will create in user directory, 
    # if there is no other location accessible for writing.
    try:
        datadir = common.selectDatadir(datadirs)
    except Exception, e:
        # When no datadir exists or exists without write access
        common.log(e, 'ERROR')
        common.log("Creating new data directory in '%s'" % DATADIR_USER )
        try:
            os.mkdir(os.path.expanduser(DATADIR_USER))
            datadir = DATADIR_USER
        except OSError, e:
            common.log(e, 'ERROR')
            sys.exit(-1)

    # Load all plugins
    # Load string names of plugins from config and retrieve its object representations
    try:
        plugins = common.loadPlugins(common.string2list(config.get('global', 'plugins')))
    except ConfigParser.NoOptionError:
        plugins = {}
    
    opt = common.mergeOptions(config, options)
    
    # DO EVERYTHING HERE
    TorUtil.loglevel = opt['tordebug']
    
    # Create URL Queue. Every URL added to queue will be processed by scanner
    urldisp = urldispatcher.urlDispatcher(opt)
    threaddisp = threaddispatcher.threadDispatcher(opt)
    torctl = sockctl.Controller(opt['torhost'], \
                                 int(opt['torcontrolport']), \
                                 opt['torcontrolpwd'])
    pathdisp = pathdispatcher.pathDispatcher(opt, torctl)
    
    #FIXME: Temporary contruction to override config settings
    options.source='urllist.txt'        
    
    sys.exit()
    
    # Run XML-RPC controlling server 
    server = rpcserver.RPCServer(name='rpcserver')
    server.opt = opt
    server.urldisp = urldisp
    server.threaddisp = threaddisp
    server.enabled = bool(int(opt['enableserver'])) 
    if server.enabled:
        server.start()
    
    # If given source file, read them and put urls to queue
    if options.source:
        common.log('Loading URLs from source file...', 'INFO')
        sourcefp = open(options.source, 'r')
            
    i = 0
    url = None
    xxxx = None
    while(1):

        # Source file is read line by line in each mainloop iteration.
        # Don't hurry, processing of one URL takes much more than
        # one loop iteration ;-).
        if options.source and sourcefp:
            if not url: # not None, when last submit was unsuccesfull
                url = sourcefp.readline().replace("\n", '')
            if url != '':
                if urldisp.submit(url):
                    # Url was accepted to queue
                    url = None
            else:
                sourcefp.close()
                sourcefp = None

        #for xx in urldisp.urls:
        #    print "%s: %d" % (urldisp.urls[xx].url, urldisp.urls[xx].status)
        #print xxxx

        # Prototype of removing URLs from queue
        # Just for testing purposes.            
        if xxxx != None: xxxx.setDone()
        xxxx = urldisp.getOne()
        
        # Check, if all threads are responding.
        # If not, kill them and run new one.
        threaddisp.checkThreads()
        
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            common.log('Pressed Ctrl+C, exiting....')
            break
        
        if False:
            common.log('%03d, TODO: %d, WORK: %d, DONE: %d' % \
                (i, urldisp.counter.todo, urldisp.counter.work, \
                urldisp.counter.done), 'INFO')
            
        i+=1
   
        # If RPC server was running and currently not,
        # shutdown application immediately.
        if server.enabled and not server.isAlive():
            break;
    
        # If application was not started as daemon (RPC server)
        # and there is no jobs in urlQueue (from --source directive),
        # shutdown
        if not server.enabled and urldisp.allDone():
            break;
        
    if server.enabled and server.isAlive():
        server.shutdown()
        common.log('XML-RPC server shutdown OK.', 'INFO')
        
    common.log('TorScanner succesfully finished at %s UTC.' %\
               time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), 'CMD')
    sys.exit(42)