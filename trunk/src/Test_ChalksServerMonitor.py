#!/usr/bin/env python2.3
# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:rodrigob.20040912211426:@thin Test_ChalksServerMonitor.py
#@@first
#@@first
#@@language python


import unittest
from Chalks import ChalksServerMonitor

#@+others
#@+node:rodrigob.20040912211426.2:class Monitor
class Monitor(unittest.TestCase):
    #@	@+others
    #@+node:rodrigob.20040912211426.3:testLaunchAndClose
    def testLaunchAndClose(self):
        sm = ChalksServerMonitor()
        sm.stop()
        return
        
    #@-node:rodrigob.20040912211426.3:testLaunchAndClose
    #@+node:rodrigob.20040912211426.4:testGetEmptyServers
    def testGetEmptyServers(self):
        sm = ChalksServerMonitor()
        servers = sm.getServers()
        assert not len(servers)
        sm.stop()
        return
        
    #@nonl
    #@-node:rodrigob.20040912211426.4:testGetEmptyServers
    #@+node:rodrigob.20040912211426.5:testGetServers
    def testGetServers(self):
        sm = ChalksServerMonitor()
        sm.registerService('test server', '127.0.0.1', 8888, "test dude")
        sm.registerService('test server 2', '127.0.0.1', 8888, "test dude")
        servers = sm.getServers()
        assert len(servers) == 2
        sm.stop()
        return
        
    #@nonl
    #@-node:rodrigob.20040912211426.5:testGetServers
    #@-others
#@-node:rodrigob.20040912211426.2:class Monitor
#@-others

if __name__ == '__main__':
  unittest.main()
#@nonl
#@-node:rodrigob.20040912211426:@thin Test_ChalksServerMonitor.py
#@-leo
