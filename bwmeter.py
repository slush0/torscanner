#!/usr/bin/env python

# Helper program for showing actual bandwidth of Tor server.
# Shows actual Read/Writes (last second), average R/W (last minute)
# and bytes left of accounting period.
# Author: Marek Palatinus
# Licence: GPL

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib-ext'))

from TorCtl import *
import socket
import time

# Settings
host = 'localhost'
port = 9051
password = ''

######## THERE ARE LIONS ######################

class avgrw:
    def __init__(self):
        self.read = 0
        self.written = 0
        self.readList = []
        self.writtenList = []
        self.period = 60

    def add(self, read, written):
        self.readList.append(read)
        self.writtenList.append(written)
        
        if len(self.readList) > self.period:
            self.readList.pop(0)
        if len(self.writtenList) > self.period:
            self.writtenList.pop(0)

        self.read = 0
        for i in self.readList:
            self.read += i
        self.read = self.read / float(len(self.readList))

        self.written = 0
        for i in self.writtenList:
            self.written += i
        self.written = self.written / float(len(self.writtenList))

class BWHandler(EventHandler):
    def __init__(self):
        EventHandler.__init__(self)
        self.avgrw = avgrw()

    def bandwidth_event(self, event):
        global ctl

        left = ctl.get_info('accounting/bytes-left')['accounting/bytes-left'].split(' ')
        left[0] = int(left[0]) / 1024. / 1024.
        left[1] = int(left[1]) / 1024. / 1024.

        self.avgrw.add(event.read/1024, event.written/1024)
        print("R: %.02f kB/s,\tW: %.02f kB/s\t| AVG R: %.02f kB/s,\tW: %.02f kB/s\t| LEFT R: %.03f MB,\tW: %.03f MB    "   %\
              (event.read/1024., event.written/1024., self.avgrw.read, \
               self.avgrw.written, left[0], left[1]))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
ctl = Connection(s)

ctl.set_event_handler(BWHandler())
th = ctl.launch_thread()
ctl.authenticate(password)
ctl.set_events(['BW'])

print "Press Ctrl+C to close program."

try:
    while 1:
	       time.sleep(1)
except KeyboardInterrupt:
    print "Shutting down...."
    s.close()
