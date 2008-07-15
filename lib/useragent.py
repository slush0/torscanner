#!/usr/env python
'''
This script download user-agents from useragentstring.com.
Use on your own risk - there is no confirmation from site owners, that you
can download and re-use user-agent strings in your application.

Don't use this script very often
Script author: Marek Palatinus, 2008
Script licence: GPL v3
'''

#__import__('httplib', globals(),  locals(), [], -1)
#import socks

import httplib
import time
import re

bots = ['bot', 'spider', 'agent', 'find', 'archive', 'crawler', 'seek']

def getUserAgents(filename):
    fp = open(filename, 'a')
    conn = httplib.HTTPConnection("www.useragentstring.com")
#    proxy = socks.socksocket()
#    proxy.setproxy(socks.PROXY_TYPE_SOCKS5, 'localhost', 9059)
#    conn.sock = proxy

    counter = 0
    exitcounter = 0
    while 1:
        if exitcounter >= 10:
            print "User-agent not found %d-times. Looks like end of DB. Closing." % exitcounter
            break
        
        conn.request("GET", '/index.php?id=%d' % counter)
        r = conn.getresponse()
        if r.status != 200:
            print 'Stopping at index %d, HTTP response %d' % (counter, r.status)
            break;
        
        data = r.read()
        if data.find('The User Agent String you selected:') == -1:
            print 'Stopping at index %d, User-Agent not found.' % (counter)
            counter += 1
            exitcounter += 1
            continue
        

        s = re.search("<textarea name='uas' id='uas_textfeld' rows='4' cols='30'>(.*)</textarea>", data)
        ua = s.groups()[0]
        
        if (True in map(lambda x: x in ua.lower(), bots)):
            print "Ignoring '%s', looks like bot" % ua
            counter += 1
            continue

        print "%d %s" % (counter, s.groups()[0])
        fp.write("%s\n" % s.groups()[0])
        fp.flush()
        
        time.sleep(0.1)
        counter += 1
        exitcounter = 0
        
    conn.close()
    fp.close()
    
# If running standalone, retrieve user agents to local file
if __name__ == '__main__':
    getUserAgents('useragent.txt')
