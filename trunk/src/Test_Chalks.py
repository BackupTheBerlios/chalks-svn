#!/usr/bin/env python2.3
# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:rodrigob.20040125173910:@thin Test_Chalks.py
#@@first
#@@first
#@@language python


#@+at
# Automatic tests and tests setup for Chalks.
#@-at
#@@c

import Chalks
from twisted.internet import reactor
from twisted.python   import usage

# see Twisted/Doc/How-to/Utilities/Parsing command-lines for the usage.Options class documentation
class Options(usage.Options):

    optFlags = [
        ["fast", "f", "Run quickly"],
        ["good", "g", "Don't validate input"],
        ["cheap", "c", "Use cheap resources"]
    ]
    optParameters = [["user", "u", None, "The user name"]]

config = Options()
try:
    config.parseOptions() # When given no argument, parses sys.argv[1:]
except usage.UsageError, errortext:
    print '%s: %s' % (sys.argv[0], errortext)
    print '%s: Try --help for usage details.' % (sys.argv[0])
    sys.exit(1)

if config['user'] is not None:
    print "Hello", config['user']

if len(config): # more than one option
    print "So, you want it:"

if config['fast']:
    print "fast",
if config['good']:
    print "good",
if config['cheap']:
    print "cheap",
print

print "Creating three Chalks instaces"
app1 = Chalks.Chalks()
app2 = Chalks.Chalks()
app3 = Chalks.Chalks()

print "Connecting app2 and app3 to app1"
app2.node.connect_to_parent("127.0.0.1", app1.chalks_service.port, "app2")
app3.node.connect_to_parent("127.0.0.1", app1.chalks_service.port, "app3")

reactor.run()
#@nonl
#@-node:rodrigob.20040125173910:@thin Test_Chalks.py
#@-leo
