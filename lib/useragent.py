#!/usr/env python
'''
This script download user-agents from useragentstring.com.
Use on your own risk - there is no confirmation from site owners, that you
can download and re-use user-agent strings in your application.

Don't use this script very often
Script author: slush <slush at centrum dot cz>, 2008
Script licence: GPL v3
'''

import httplib
import time
import re
import random

bots = ['bot', 'spider', 'agent', 'find', 'archive', 'crawler', 'seek']

def getRandomUserAgent(fromIndex=0, toIndex=9000):
    '''Takes random user agent from database. Try to find ten-times, when
    random record not found or if it looks like some bot.'''
    conn = _connect()
    counter = 0
    while counter<10:
        index = random.randint(fromIndex, toIndex)
        agent = _getAgent(conn, index)
        if agent != False: break
        counter += 1
    _close(conn)
    return agent
    
def getAllUserAgents(filename):
    '''Download ALL user-agents from site. Might run very long time. Be careful.'''
    fp = open(filename, 'a')
    conn = _connect()

    counter = 0
    exitcounter = 0
    while 1:
        if exitcounter >= 10:
            print "User-agent not found %d-times. Looks like end of DB. Closing." % exitcounter
            break
        
        agent = _getAgent(conn, counter)
        if not agent:
            counter += 1
            exitcounter += 1
            continue

        print "%d %s" % (counter, agent)
        fp.write("%s\n" % agent)
        fp.flush()
        
        time.sleep(0.1)
        counter += 1
        exitcounter = 0
        
    _close(conn)
    fp.close()

def _connect():
     return httplib.HTTPConnection("www.useragentstring.com")
#    proxy = socks.socksocket()
#    proxy.setproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9059)
#    conn.sock = proxy

def _getAgent(conn, index):
    conn.request("GET", '/index.php?id=%d' % index)
    r = conn.getresponse()
    if r.status != 200:
        print 'Index %d not found, HTTP response %d' % (index, r.status)
        return False
    
    data = r.read()
    if data.find('The User Agent String you selected:') == -1:
        print 'Index %d not found, problem in parsing \'User-Agent\'.' % (index)
        return False

    s = re.search("<textarea name='uas' id='uas_textfeld' rows='4' cols='30'>(.*)</textarea>", data)
    ua = s.groups()[0]
    
    if (True in map(lambda x: x in ua.lower(), bots)):
        print "Ignoring '%s', looks like bot" % ua
        return False
    
    return ua

def _close(conn):
    conn.close()

# If running standalone, retrieve user agents to local file
if __name__ == '__main__':
    getAllUserAgents('useragent.txt')
