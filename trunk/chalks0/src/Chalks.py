#!/usr/bin/env python2.3
# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:rodrigob.20040119132914:@thin Chalks.py
#@@first
#@@first
#@@language python

#@+at
# Chalks is a simplified LeoN application. Intended to give ultra easy usage 
# in order to allow massive employment of this technology.
# This program is one pure python package. Most of the code is derived from 
# LeoN and Leo base code.
# http://souvenirs.sf.net
# http://leo.sf.net
# 
# 31/05/03 LeoN started. RodrigoB.
# 19/01/04 Started LeoN spinoff. RodrigoB.
# 27/01/04 Renamed MultiEdit as Chalks. Working. RodrigoB.
# 20/02/04 Frozen. RodrigoB.
# 25/08/04 Project resurrected. Ricardo Niederberger Cabral joined development 
# efforts. Logs are now kept in the berlios svn server.
#@-at
#@@c

### Check twisted version
try:
    from twisted.copyright import version as twistedVersion
    twistedIntVersion = [int(x[0]) for x in twistedVersion.split('.')]
    if (twistedIntVersion[0] >= 2) or (twistedIntVersion[0] >= 1 and twistedIntVersion[1] >= 3):
        pass # Twisted version > 1.3 correct
    else:
        print "Chalks requires Twisted 1.3 or superior. Download it from http://www.twistedmatrix.com"
        sys.exit(1)
except:
    print 'Error detecting Twisted version. Perhaps you are running a CVS/SVN version. Continuing anyway.'

# Tkinter Imports
from Tkinter import *
from Tkconstants import *

# Twisted imports
from twisted.internet import tksupport # the first thing that we need to do is to install the Tkinter loop.
from twisted.internet import reactor
from twisted.python import components

  
#@+at 
#@nonl
# # THIS IS CURRENTLY DISABLED
# # Woven imports
# from twisted.web.woven import page, interfaces, model
# from twisted.web import server
#@-at
#@@c

# Twisted Applications imports
from twisted.application import service, internet

# Perspective Broker imports
from twisted.cred import checkers, portal, credentials, error
from twisted.spread import pb
from twisted.python import failure

# python imports
import time


# globals
global dbg
dbg = 0
#@+others
#@+node:rodrigob.20040119133203:Theorical aspects
#@+at
# (explain the collaborative edition concept, how it is achieved)
# (explain how the multi node system is achieved)
# (enforce KIS orientation)
#@-at
#@@c
#@nonl
#@+node:rodrigob.20040126020116:network graph (about Server, Client, Children, Parent, and Trees)
#@+at
# The network graph is a Tree.
# The upper node is the first instance, that created the original content.
# Down tree we found the other sessions.
# Each node has one parent and possibly many childrens.
#@-at
#@@c
#@nonl
#@-node:rodrigob.20040126020116:network graph (about Server, Client, Children, Parent, and Trees)
#@+node:rodrigob.20040125194054:repetitions (personal note)
#@+at
# We allow nodes to connect to us. We are connected to at most one node.
# 
# When we generate an operation we send it to all known site.
# When we receive operations from a site, we repeat it to allow other known 
# ones.
# 
# 
# self.nodes
# 
#@-at
#@@c
#@nonl
#@-node:rodrigob.20040125194054:repetitions (personal note)
#@-node:rodrigob.20040119133203:Theorical aspects
#@+node:rodrigob.20040129130513:helpers
#@+at
# Miscelaneous functions that help doing common actions
#@-at
#@@c


def guess_username():
    """
    Guess a login name
    """
    from os import getenv
    return str(getenv('username') or getenv('USER'))
#@nonl
#@-node:rodrigob.20040129130513:helpers
#@+node:rodrigob.20040119152542:class Chalks
class Chalks:
    """
    Main class that builds the Graphical User Interface and contains other interactive objects, such as the CollaborativeEditableNode.
    This class takes care mainly of the GUI. Other tasks are delegated (components architecture, has-a architecture).
    """
    
    #@    @+others
    #@+node:rodrigob.20040123131236:__init__
    def __init__(self, web_service=1):
        """
        At the instanciation create the gui and install the reactor support
        """
        
        root = Tk()
        tksupport.install(root) # Install the Reactor support
        self.body(root) # build the gui
       
        self.encoding = "utf-8" # is this standard, sustainable ?
        self.version = '0.0.1'
        
        
        self.file     = None # will keep the file instance
        self.filename = None # will keep the filename
        self.service_name = None # will keep the name for the currently advertised service
        self.saved_version_hash = hash("\n") # used to check changes in the file
        
        print "Chalks " + self.version + ", started. Licensed under the GNU GPL. Copyright 2004, Chalks Development Team (http://chalks.berlios.de)\n"
        
        #@    << install the web service >>
        #@+node:rodrigob.20040125150558:<< install the web service >>
        # install the web service
        #NOTE: this is currently disabled
        #@+at
        # if 0 and web_service:
        #     site = server.Site(utf8Page(interfaces.IModel(self), 
        # templateFile="Chalks.xhtml", templateDirectory="./"))
        #     web_portno = pb.portno + 1
        #     for port in xrange(web_portno, web_portno+10):
        #         try:
        #             web_service = reactor.listenTCP(port, site) 
        # #internet.TCPServer(port, site).setParentApp(app)
        #         except: # failed
        #             continue
        #         else: # got it
        #             print "Starting web service at http://localhost:%i" % 
        # port
        #             #print "%s %s" % (web_service, dir(web_service))
        #             self.web_service = web_service
        #             break # stop creating web services
        #     else: # the range failed
        #         self.log_error("Could not find an available port in the 
        # range %s to provide webpublishing of the text contents." % 
        # [web_portno, web_portno+10])
        #@-at
        #@nonl
        #@-node:rodrigob.20040125150558:<< install the web service >>
        #@nl
        #@    << install the collaboration service >>
        #@+node:rodrigob.20040125153141:<< install the collaboration service >>
        # install the collaboration service 
        
        self.node = ChalksNode(self) # ChalksNode takes care of the rest
        
        # local PB classes definitions
        #@+others
        #@+node:rodrigob.20040125200531.1:Chalks realm
        class ChalksRealm:
            """
            Provide access to a ChalksAvatar
            """
            __implements__ = portal.IRealm
                                             
            def __init__(self, chalks_gui):
                self.chalks_gui = chalks_gui                                                                                                                             
            def requestAvatar(self, avatarId, mind, *interfaces):
                if pb.IPerspective in interfaces:
                    avatar = ChalksAvatar(avatarId, mind, self.chalks_gui)
                    return pb.IPerspective, avatar, avatar.logout
                else:
                    raise NotImplementedError("no interface")
        
        #@-node:rodrigob.20040125200531.1:Chalks realm
        #@+node:rodrigob.20040125200531:dummy checker
        class DummyChecker:
            """
            gives access to everyone
            """
            __implements__ = checkers.ICredentialsChecker
        
            credentialInterfaces = (credentials.IUsernamePassword, credentials.IUsernameHashedPassword)
        
            def requestAvatarId(self, credential):		
                """
                give access to everyone that requests it
                """
                if 1:
                    return credential.username
                else:
                    return failure.Failure(error.UnauthorizedLogin("'%s' is not listed in the authorized users list." % credential.username))
        
        #@-node:rodrigob.20040125200531:dummy checker
        #@-others
        
        self.server_port = None # initially we don't know which port we are serving at
        
        t_portal = portal.Portal(ChalksRealm(self))
        t_portal.registerChecker(DummyChecker())
        pb_factory = pb.PBServerFactory(t_portal)
        
        for port in xrange(pb.portno, pb.portno+10):
            try:
                pb_service = reactor.listenTCP(port, pb_factory) #internet.TCPServer(port, site).setParentApp(app)
            except: # failed
                continue
            else: # got it
                self.server_port = port
                print "Starting Chalks service at chalks://localhost:%i" % port
                #print "Knowing your internet address (i.e. your IP) other users can connect themself to your session using the port %i." % port  #<<<<< this should be replaced by a friendlier popup or message
                self.chalks_service = pb_service
                break # stop creating web services
                
        else: # the range failed
            self.log_error("Unable to find an available port in the range %s to provide the chalks service." % [pb.portno, pb.portno+10] )
            self.log_error("This is a fatal error")
            self.text_widget["state"] = DISABLED # I said fatal error...
            
        #@nonl
        #@-node:rodrigob.20040125153141:<< install the collaboration service >>
        #@nl
        #@    << guess local ip address >>
        #@+node:niederberger.20040826214344:<< guess local ip address >>
        #@+at
        # this method relies on an external perl script hosted on any cgi-bin 
        # environment to guess the correct external ip address.
        # This is definitely not needed for NAT'd nodes.
        #@-at
        #@@c
        
        self.log("Guessing your IP address...\n")
        
        t_onError='127.0.0.1'
        t_adr = "http://imgseek.sourceforge.net/cgi-bin/getMyAddress.pl"
        
        def ip_callback(value):
            print "Your external IP address is '%s'"%value
            
        def ip_errback(error):
            print "Unable to determine IP address. Setting to '%s'" % t_onError
        
        from twisted.web.client import getPage
        getPage(t_adr).addCallbacks( callback=ip_callback, errback=ip_errback )
        
        #@-node:niederberger.20040826214344:<< guess local ip address >>
        #@nl
        #@    << install server monitor >>
        #@+node:niederberger.20040911103457:<< install server monitor >>
        #@+at
        # install server monitor and advertise this Chalks server
        #@-at
        #@@c
        self.server_monitor = None
        try:
            self.server_monitor = ChalksServerMonitor()
        except:
            print "Could not start ZeroConf service. Working without it."
        #@-node:niederberger.20040911103457:<< install server monitor >>
        #@nl
        #@    << advertise local server >>
        #@+node:niederberger.20040911111958:<< advertise local server >>
        if self.server_port and self.server_monitor: #only if we actually started serving
            # first determine local ip address
            import socket
            self.server_address = socket.gethostbyname(socket.gethostname())
        
            # now advertise
            user_name = guess_username() +'@'+ socket.gethostname()  # this seems to work fine under Win32 and Linux
            
            # the service name should be "<file name> at <machine name>", but at this point we have no file name, so just name it something random
            import random
            self.service_name = user_name + ' Chalks server ' + str(random.randint(1,100000))
            
            self.server_monitor.registerService(self.service_name, self.server_address, self.server_port, user_name)
        #@-node:niederberger.20040911111958:<< advertise local server >>
        #@nl
    
    #@-node:rodrigob.20040123131236:__init__
    #@+node:rodrigob.20040123131236.1:quit
    
    def quit(self, *args):
        """
        """
        # ask if we need to save the file
        
        if self.is_dirty(): # if file is dirty
            if self.filename: 
                message = "File %s contains changes not yet saved to disk.\nDo you want to save the file before quiting ?" % self.filename
            else:
                message = "The text has not been saved. Save before exit ?"
            
            ret = self.askYesNoCancel("Save and exit", message) # ret 1, 0 or -1 for cancel
        
            if ret == 1:
                # save the file
                ret = self.onSave()
                if not ret: # did not saved
                    return # do not quit
    
            elif ret == -1:
                print "you canceled"
                return
                
        if self.server_monitor:
            # shutdown Server Monitor
            self.server_monitor.stop()
        
        # non return point, the app will quit
        reactor.stop()
        print "Thanks for using Chalks, have a nice day.\n"
        return
            
    
    #@-node:rodrigob.20040123131236.1:quit
    #@+node:rodrigob.20040123142302:helpers
    #@+at
    # Miscelaneous methods and classes that help to do common actions
    #@-at
    #@@c
    #@nonl
    #@+node:niederberger.20040826214731:is_firewalled
    def is_firewalled(self):
        """check if this machine is firewalled or nat'd
        -1 means 'unable to determine with this test'
        """
        def getstatusoutput(cmd): #python commands.py is broken on nt/xp systems, since {cmd} is not supported by cmd.exe
            """Return (status, output) of executing cmd in a shell."""
            import os
    
            if (os.name == 'nt'):
                pipe = os.popen(cmd + ' 2>&1', 'r')
            else:
                pipe = os.popen('{ ' + cmd + '; } 2>&1', 'r')
    
            text = pipe.read()
            sts = pipe.close()
            if sts is None: sts = 0
            if text[-1:] == '\n': text = text[:-1]
            return sts, text
    
        import sys
        gateway_column = 1
        if sys.platform == 'win32':
            gateway_column = 2
        else:
            gateway_column = 1
    
        error = 0
        try:
            data = getstatusoutput('netstat -rn')
            if data[0]:
                return -1
            data = data[1]
            data = data.split('\n')
            for line in data:
                if not line:
                    break
    
                t_list = line.split()
                if len(t_list) < 3:
                    continue
    
                #if t_list[2] == '0.0.0.0':   # genmask == this -> default gw
    
                # linux2:
                #  Destination Gateway  Genmask ...
                #  0.0.0.0     10.0.0.1 0.0.0.0
                # freebsd4:
                #  Destination Gateway  Flags, ...
                #  default     10.0.0.1 ...
                # win32:
                #  Net-addr    Netmask  Gateway   Interface  Metric
                #  0.0.0.0
    
                # RFC 1918 specifies 10., 172.16., 192.168.
                # DHCP uses 169.254. (?)
    
                if t_list[2] == '0.0.0.0' or t_list[0] == 'default' or t_list[0] == '0.0.0.0':
                    for prefix in [ '10.', '172.16.', '192.168.', '169.254.' ]:
                        if t_list[gateway_column][:len(prefix)] == prefix:
                            error = 1
        except:
            self.log_error("error while figuring out if local machine is firewalled")
    
        return error
    #@-node:niederberger.20040826214731:is_firewalled
    #@+node:rodrigob.20040129131141:set_encoding
    #@+at 
    #@nonl
    # According to Martin v. Löwis, getdefaultlocale() is broken, and cannot 
    # be fixed. The workaround is to copy the getpreferredencoding() function 
    # from locale.py in Python 2.3a2.  This function is now in leoGlobals.py.
    #@-at
    #@@c
    
    def set_encoding (self):    	
        """Set app.tkEncoding."""
        #<<<<< finish
        raise NotImplementedError
    
        for (encoding,src) in (
            ("utf-8","default")
            (self.config.tkEncoding,"config"),
            #(locale.getdefaultlocale()[1],"locale"),
            (getpreferredencoding(),"locale"),
            (sys.getdefaultencoding(),"sys"),
            ("utf-8","default")):
            if isValidEncoding (encoding): # 3/22/03
                self.tkEncoding = encoding
                # trace(self.tkEncoding,src)
                break
            elif encoding and len(encoding) > 0:
                trace("ignoring invalid " + src + " encoding: " + `encoding`)
                
        color = choose(self.tkEncoding=="ascii","red","blue")
    #@nonl
    #@-node:rodrigob.20040129131141:set_encoding
    #@+node:rodrigob.20040125204408:is dirty
    def is_dirty(self):
        """
        Indicates if the contents of the file have changed since last saved.
        Uses a hash function
        """
        
        return self.saved_version_hash != hash(self.text_widget.get("1.0", END))
    #@nonl
    #@-node:rodrigob.20040125204408:is dirty
    #@-node:rodrigob.20040123142302:helpers
    #@+node:rodrigob.20040123133012:log
    def log(self, text, tag=None, color=None):
        """
        log some text in the log panel
        """
        assert hasattr(self, "log_widget")
        assert hasattr(self, "status_text")
    
        if tag:   assert type(tag)   is str
        if color: assert type(color) is str
        
        self.log_widget.config(state=NORMAL)                    
    
        if color:
            self.log_widget.tag_config(color, foreground=color) # create or config a tag to have the same name that the color string
            tag = color
                        
        if tag:
            t_index = self.log_widget.index(INSERT)
            self.log_widget.insert(END, text)
            self.log_widget.tag_add(tag, t_index, END)
        else:
            self.log_widget.insert(END, text)
            
        self.log_widget.config(state=DISABLED)
        
        self.log_widget.yview(END) # makes sure the bottom is visible
        
        # we also keep the last message in the status bar
        self.set_status(text)
            
        return
        
    
    #@+node:rodrigob.20040123134959:log_error
    def log_error(self, text):
        """
        log an error
        """ 
        return self.log("<error> %s" % text, tag="error")
    #@-node:rodrigob.20040123134959:log_error
    #@+node:rodrigob.20040128005315:exception
    def exception(self, error):
        """
        manage the exceptions
        'error' should be a Failure (or subclass) holding the MyError exception, 
        error.{type , getErrorMessage, __class__, getBriefTraceback, getTraceback}
        """	
        
        #error.trap(ChalksError) # to manage silently that exceptions
        #raise error # raise the remote error, short error message (brief traceback)
        
        # "<Error!> Got a remote Exception\n<%s><%s> %s " 
        self.log_error( "<Error!><%s>\n%s"%(error.type, error.getErrorMessage()) )
        self.log_error( "<Debug> %s"% error.getTraceback()) # only for debugging
        return
    
    
    
    #@-node:rodrigob.20040128005315:exception
    #@+node:rodrigob.20040124165851:set_status
    def set_status(self, text):
        """
        set the text of the status bar
        """
        
        t_widget = self.status_text
        t_widget.config(state=NORMAL)
        t_widget.delete("1.0", END)
        t_widget.insert(END, text)
        t_widget.config(state=DISABLED)
        
        return
    #@-node:rodrigob.20040124165851:set_status
    #@-node:rodrigob.20040123133012:log
    #@+node:rodrigob.20040121151612:body (construct the gui)
    def body(self, base_frame):
        """
        build the body of the dialog window
        """
        
        # base_frame
        self.root = root = base_frame    
        
        #@    << create frames >>
        #@+node:rodrigob.20040122173046:<< create frames >>
        #f = Frame(root,bd=0,relief="flat")
        #f.pack(expand=1,fill="both",pady=1)
        #pane1 = Frame(f)
        #pane2 = Frame(f)
        #bar =   Frame(f,bd=2,relief="raised",bg="LightSteelBlue2")
        
        self.splitVerticalFlag = 1 # self.splitVerticalFlag tells the alignment of the splitter 
        verticalFlag = 1
        #@<< create the splitter >>
        #@+node:rodrigob.20040123123802.1:<< create the splitter >>
        # Create a splitter window and panes into which the caller packs widgets.
        # Returns (f, bar, pane1, pane2) 
        
        parent = root
        
        # require parent, verticalFlag
        
        # set up icon only on win32 (need to research how this is done on *NIX)
        import sys
        if sys.platform == 'win32':
            root.iconbitmap(bitmap="chalks.ico")  # set application icon
        
        # Create the frames.
        f = Frame(parent,bd=0,relief="flat",width=640,height=480) # without forcing width/height, the frame starts up with a really small dimension on win32 (almost iconic)
        f.pack(expand=1,fill="both",pady=1)
        pane1 = Frame(f)
        pane2 = Frame(f)
        bar =   Frame(f,bd=2,relief="raised",bg="LightSteelBlue2")
        
        # Configure and place the frames.
        
        #@<< configure >>
        #@+node:rodrigob.20040123123829:<< configure >>
        #bar, verticalFlag
        
        
        w = 7
        relief = "groove"
        color = "LightSteelBlue2"
        
        try:
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(relief=relief,height=w,bg=color,cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(relief=relief,width=w,bg=color,cursor="sb_h_double_arrow")
        except: # Could be a user error. Use all defaults
            self.log("exception in user configuration for splitbar")
        
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(height=7,cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(width=7,cursor="sb_h_double_arrow")
        
        
        # bind the bar
        bar.bind("<B1-Motion>", self.onDragSplitBar)
        #@-node:rodrigob.20040123123829:<< configure >>
        #@nl
        #@<< place >>
        #@+node:rodrigob.20040123130224.1:<< place >>
        #bar,pane1,pane2,verticalFlag
        
        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            pane1.place(relx=0.5, rely =   0, anchor="n", relwidth=1.0, relheight=0.5)
            pane2.place(relx=0.5, rely = 1.0, anchor="s", relwidth=1.0, relheight=0.5)
            bar.place  (relx=0.5, rely = 0.5, anchor="c", relwidth=1.0)
        else:
            # Panes arranged horizontally; vertical splitter bar
            # adj gives tree pane more room when tiling vertically.
            adj = (verticalFlag != self.splitVerticalFlag and 0.65) or 0.5
            pane1.place(rely=0.5, relx =   0, anchor="w", relheight=1.0, relwidth=adj)
            pane2.place(rely=0.5, relx = 1.0, anchor="e", relheight=1.0, relwidth=1.0-adj)
            bar.place  (rely=0.5, relx = adj, anchor="c", relheight=1.0)
        #@nonl
        #@-node:rodrigob.20040123130224.1:<< place >>
        #@nl
        
        #return f, bar, pane1, pane2
        #@-node:rodrigob.20040123123802.1:<< create the splitter >>
        #@nl
        self.split_bar, self.splitPane1, self.splitPane2 = bar, pane1, pane2
        self.resizePanesToRatio(1.0/4)
        
        
        # create the body and the chat frames
        from ScrolledText import ScrolledText
        #@<< create the log  widget >>
        #@+node:rodrigob.20040125153909:<< create the log widget >>
        self.log_widget  = ScrolledText(pane1, background="white", state=DISABLED)
        self.log_widget["height"] = 1
        self.log_widget.pack(fill=BOTH, expand=1)
        self.log_widget.tag_config("error", foreground="red")
        #@-node:rodrigob.20040125153909:<< create the log widget >>
        #@nl
        #@<< create the text widget >>
        #@+node:rodrigob.20040125153909.1:<< create the text widget >>
        self.text_widget = text_widget = ScrolledText(pane2, background="white", height=0)
        text_widget.pack(fill=BOTH, expand=1)
        
        # Event handlers...
        #text_widget.bind("<Button-1>", self.onTextClick)
        #text_widget.bind("<Button-3>", self.onTextRClick)
        #text_widget.bind("<Double-Button-1>", self.onTextDoubleClick)
        text_widget.bind("<Key>", self.onTextKey)
        
        # Returns < < s > >
        def virtual_event_name(s):
            return ( "<<" + s +
                   ">>") # must be on a separate line.
        
        # Gui-dependent commands...
        text_widget.bind(virtual_event_name("Cut"), self.onCut)
        text_widget.bind(virtual_event_name("Copy"), self.onCopy)
        text_widget.bind(virtual_event_name("Paste"), self.onPaste)
        #@nonl
        #@-node:rodrigob.20040125153909.1:<< create the text widget >>
        #@nl
        
        #@-node:rodrigob.20040122173046:<< create frames >>
        #@nl
        #@    << install the menu >>
        #@+node:rodrigob.20040122173046.1:<< install the menu >>
        
        self.menu_bar = Menu(root,)
        
        # File, Save, Open, Connect to; Help, about, help, online homepage
        
        self.file_menu = file_menu = Menu(self.menu_bar,)
        
        file_menu.add_command(label="Connect to", underline=0, accelerator="Ctrl+T", command= self.onConnectTo)
        file_menu.add_separator()
        file_menu.add_command(label="Open", underline=0, accelerator="Ctrl+O",command= self.onOpen)
        file_menu.add_command(label="Save", underline=0, accelerator="Ctrl+S", command= self.onSave)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", underline=0,  accelerator="Ctrl+Q", command= self.quit)
        
        self.menu_bar.add_cascade(label = "File", underline=0, menu= file_menu)
        
        self.menu_bar.add_command(label="Help", underline=0, command= self.onHelp)
        #@+at
        # help_menu = Menu(self.menu_bar,)
        # help_menu.add_command(label="About", command= lambda _: None)
        # help_menu.add_command(label="Help", command= lambda _: None)
        # help_menu.add_command(label="Online homepage", command= 
        # self.online_homepage)
        # 
        # self.menu_bar.add_cascade(label = "Help", menu= help_menu)
        #@-at
        #@@c
        
        root.config(menu=self.menu_bar)
        
        
        # install the shortcuts
        root.bind("<Control-t>", self.onConnectTo)
        root.bind("<Control-o>", self.onOpen)
        root.bind("<Control-s>", self.onSave)
        root.bind("<Control-q>", self.quit)
        root.bind("<Control-H>", self.onHelp)
        #@-node:rodrigob.20040122173046.1:<< install the menu >>
        #@nl
        #@    << install the status bar >>
        #@+node:rodrigob.20040122173046.3:<< install the status bar >>
        #@+others
        #@-others
        
        self.status_bar = Frame(pane2, bd=2)
        
        self.rowcol_stringvar = StringVar()
        self.rowcol_label = Label(self.status_bar, textvariable=self.rowcol_stringvar, anchor=W)
        self.rowcol_label.pack(side=LEFT, padx=1)
        
        bg = self.status_bar.cget("background")
        self.status_text = Text(self.status_bar, height=1, state=DISABLED, bg=bg, relief=GROOVE)
        self.status_text.pack(side=LEFT, fill=X,expand=1)
        
        # Register an idle-time handler to update the row and column indicators.
        self.status_bar.after_idle(self.updateStatusRowCol)
        
        
        #self.status_bar.pack(fill=X, pady=1) # the status bar is pack at onDragSplitBar
        #@nonl
        #@-node:rodrigob.20040122173046.3:<< install the status bar >>
        #@nl
        #@    << install the chat bar >>
        #@+node:rodrigob.20040122173046.2:<< install the chat bar >>
        #@+at
        # Create the chat_bar widget that is a posteriori inserted or extirped 
        # from the log panel.
        # The chat bar allow smart text entry
        #@-at
        #@@c
            
        parent = pane1
        self.chat_bar = chat_bar = Frame( parent, borderwidth=1,relief=SUNKEN)
        
        self.rowcol_label = Label(chat_bar, textvariable=self.rowcol_stringvar, anchor=W)   
        self.rowcol_label.pack(side=LEFT, padx=1)
        
        # the entry is a text widget of fixed heigth 1. The '\n' keystroke is related to a function call. then users can send lines, and have an history.
        
        log = self.log_widget
        self.chat_text_entry = text = Text(chat_bar, height=1, background = log["background"], font = log["font"])
        text.pack(side=RIGHT, fill=BOTH, expand=1)
        text.bind("<Return>", self.onChattextEntry )
        
        text.insert(END, " The chat bar is disabled until someone connects to you or you connect to someone.")
        text["state"] = DISABLED
        
        chat_bar.pack(fill=BOTH)
        #@nonl
        #@-node:rodrigob.20040122173046.2:<< install the chat bar >>
        #@nl
    
        self.Redirect(self)
        
        root.title("Chalks")
        root.protocol('WM_DELETE_WINDOW', self.quit) # not a good idea because already overwritten, has to intercept finishQuit
    
        self.text_widget.focus_set() # put the input focus at the text widget 
            
        return
    #@nonl
    #@+node:rodrigob.20040125210836:helpers
    #@+at
    # this code is at the class Chalks level
    #@-at
    #@@c
    #@nonl
    #@+node:rodrigob.20040122182446.1:class Redirect
    class Redirect:
        """
        act a proxy for a file
        When instanciated will redirect the stdout and stdout over the log_widget.
        """
        
        # To redirect stdout a class only needs to implement a write(self,s) method.
        def __init__ (self, app):
            
            assert hasattr(app, "log_widget"), "require to have already build the gui in order to install the redirection"
            
            self.redirecting = None
            self.app = app
            self.app.log_widget.tag_config("stdout", foreground="gray45")
            
            self.redirect() # redirect stderr and stdout to the log panel
            
        def isRedirected (self):
            return self.redirecting
            
        def flush(self, *args):
            return # 6/14/03:  For LeoN: just for compatibility.
        
        def redirect (self):
            import sys
            if not self.redirecting:
                sys.stdout, sys.stderr, self.redirecting = self, self, 1
        
        def undirect (self,stdout=1):
            import sys
            sys.stdout, sys.stderr, self.redirecting = sys.__stdout__, sys.__stderr__, None
    
        def write(self,s):
            if self.redirecting:
                if self.app.log_widget: 
                    if not s.isspace(): # if it has some readable content
                        self.app.log("<local> %s" % s , tag= "stdout")
                    else:
                        self.app.log(s)
    
                sys.__stdout__.write(s) # anyway write out (to see the crash errors)
            else: print s # Typically will not happen.
        
    #@-node:rodrigob.20040122182446.1:class Redirect
    #@+node:rodrigob.20040123142018:ask yes no or cancel
    def askYesNoCancel(self, title, message):
        """
        helper method to ask yes, no cancel
        """
        
        import tkMessageBox
        
        ret = tkMessageBox._show(title=title, message=message, icon=tkMessageBox.QUESTION, type=tkMessageBox.YESNOCANCEL)
        # will return .YES, .NO or .CANCEL
        #dic = {tkMessageBox.YES:1, tkMessageBox.NO:0, tkMessageBox.CANCEL:-1}
        #print "yes no cancel :", ret, type(ret) # just for debugging
        #return dic[ret] # did not work for cancel
        
        if   ret == tkMessageBox.YES: return  1
        elif ret == tkMessageBox.NO : return  0
        else:                         return -1
    #@nonl
    #@-node:rodrigob.20040123142018:ask yes no or cancel
    #@-node:rodrigob.20040125210836:helpers
    #@-node:rodrigob.20040121151612:body (construct the gui)
    #@+node:rodrigob.20040123124005:gui commands/events
    #@+node:rodrigob.20040124184444:text widget commands
    #@+at
    # Hooks related to the text widget
    #@-at
    #@@c
    
    #@+at 
    # Text Key Handlers
    # 
    # The <Key> event generates the event before the text text is changed(!), 
    # so we register an idle-event handler to do the work later.
    # 
    # 1/17/02: Rather than trying to figure out whether the control or alt 
    # keys are down, we always schedule the idle_handler.  The idle_handler 
    # sees if any change has, in fact, been made to the text text, and sets 
    # the changed and dirty bits only if so.  This is the clean and safe way.
    # 
    # 2/19/02: We must distinguish between commands like "Find, Then Change", 
    # that call onTextChanged, and commands like "Cut" and "Paste" that call 
    # onTextWillChange.  The former commands have already changed the text 
    # text, and that change must be captured immediately.  The latter commands 
    # have not changed the text, and that change may only be captured at idle 
    # time.
    #@-at
    #@@c
    
    #@+others
    #@+node:rodrigob.20040125154636:onTextKey
    def onTextKey (self,event):
        """
        Handle any key press event in the text pane.
        This method is called before the key operation is efectued.
        We recolect all the pertinent status data and use it in posterior processing.
        """
        
        # required data
        d = {}
        d["undoType"] = "Typing"
        d["ch"] = event.char
        d["keycode"] = event.keycode
        d["oldSel"]  = self.get_text_selection() 
        d["oldText"] = self.text_widget.get("1.0", END)
    
    
        # obtain some important tags positions
                
        tags_ranges = {}
        #tag_names = self.text_widget.tag_names() 
        tag_names = ["to_send"] # we are only interesed on the to_send ranges
    
        for t_name in tag_names:
            if 0:
                # normally there are only  two or fours tags at the same time
                # so we convert them directly
                tags = []
                for start, stop in self.text_widget.tag_ranges(t_name) :
                    pos = (self.text_widget.get("1.0", start))
                    length = (self.text_widget.get(start, stop))
                    tags.append((pos, length))
            else:
                tags = self.text_widget.tag_ranges(t_name)
                
            tags_ranges[t_name] = tags
    
        d["oldTagsRanges"]	= tags_ranges
        
                
        #self.log("tag names %s tags_tanges %s"%(self.text_widget.tag_names(), tags_ranges), color="orange")
        
        self.text_widget.after_idle(self.idle_text_key, d)
        
        return
    
    #@+node:rodrigob.20040125192325:get text selection
    def get_text_selection (self):
        """
        Return a tuple representing the selected range of body text.
        Return a tuple giving the insertion point if no range of text is selected.
        """
    
        text_widget = self.text_widget
        sel = text_widget.tag_ranges("sel")
    
        if len(sel) == 2:
            return sel
        else:
            # Return the insertion point if there is no selected text.
            insert = text_widget.index("insert")
            return insert,insert
    #@nonl
    #@-node:rodrigob.20040125192325:get text selection
    #@-node:rodrigob.20040125154636:onTextKey
    #@+node:rodrigob.20040125154657:idle_text_key (hook caller of ChalksNode.fill_body) 
    def idle_text_key (self, data):	
        """
        Update the text pane at idle time.
        """
        
        self.node.fill_body(data) # parse the events over the text widget
        
        return 
    #@nonl
    #@-node:rodrigob.20040125154657:idle_text_key (hook caller of ChalksNode.fill_body) 
    #@+node:rodrigob.20040125145031:Cut/Copy/Paste
    def onCut (self,event=None):
        """The handler for the virtual Cut event."""
        self.onTextWillChange("Cut")
    
    def OnCutFromMenu (self):    
        """
        called from the menu
        """
        self.root.event_generate(virtual_event_name("Cut"))
    
    
    
    def onCopy (self,event=None):
        
        # Copy never changes dirty bits or syntax coloring.
        return
            
    def OnCopyFromMenu (self):
    
        self.root.event_generate(virtual_event_name("Copy"))
    
    
    def onPaste (self,event=None):
        
        self.onTextWillChange(v,"Paste")
        
    def onPasteFromMenu (self):
    
        self.root.event_generate(virtual_event_name("Paste"))
    #@-node:rodrigob.20040125145031:Cut/Copy/Paste
    #@-others
    #@nonl
    #@-node:rodrigob.20040124184444:text widget commands
    #@+node:rodrigob.20040123130224:split bar commands
    #@+node:rodrigob.20040121150952.2:resizePanesToRatio
    def resizePanesToRatio(self,ratio):
        self.divideSplitter(self.splitVerticalFlag, ratio)
    #@-node:rodrigob.20040121150952.2:resizePanesToRatio
    #@+node:rodrigob.20040121150952.7:onDragSplitBar
    def onDragSplitBar (self, event):
        self.onDragSplitterBar(event,self.splitVerticalFlag)
    
    def onDragSplitterBar (self, event, verticalFlag):
    
        # x and y are the coordinates of the cursor relative to the bar, not the main window.
        bar = event.widget
        x = event.x
        y = event.y
        top = bar.winfo_toplevel()
    
        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            wRoot	= top.winfo_rooty()
            barRoot = bar.winfo_rooty()
            wMax	= top.winfo_height()
            offset = float(barRoot) + y - wRoot
        else:
            # Panes arranged horizontally; vertical splitter bar
            wRoot	= top.winfo_rootx()
            barRoot = bar.winfo_rootx()
            wMax	= top.winfo_width()
            offset = float(barRoot) + x - wRoot
    
        # Adjust the pixels, not the frac
        if offset < 3: offset = 3
        if offset > wMax - 2: offset = wMax - 2
        # Redraw the splitter as the drag is occuring
        frac = float(offset) / wMax
        # trace(`frac`)
        self.divideSplitter(verticalFlag, frac)
        
        
        # check if the chat bar has dissapeared or appeared, to sincronise with the status_bar
        if self.chat_bar.winfo_height() < 15 or offset < 5: 
            self.status_bar.pack(fill=X, pady=1)
            #t_text = self.text_widget.get("end - 1 line", "end")
            t_text = "this is the status bar"
            #print t_text
            self.set_status(t_text)
        else:
            self.status_bar.forget()
        
        
    #@nonl
    #@+node:rodrigob.20040121150952.6:divideSplitter
    # Divides the main or secondary splitter, using the key invariant.
    def divideSplitter (self, verticalFlag, frac):
        self.divideAnySplitter(frac, verticalFlag, self.split_bar, self.splitPane1, self.splitPane2)
        self.ratio = frac # Ratio of body pane to tree pane.
    
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.
    
    def divideAnySplitter (self, frac, verticalFlag, bar, pane1, pane2):
    
        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            bar.place(rely=frac)
            pane1.place(relheight=frac)
            pane2.place(relheight=1-frac)
        else:
            # Panes arranged horizontally; vertical splitter bar
            bar.place(relx=frac)
            pane1.place(relwidth=frac)
            pane2.place(relwidth=1-frac)
    #@nonl
    #@-node:rodrigob.20040121150952.6:divideSplitter
    #@-node:rodrigob.20040121150952.7:onDragSplitBar
    #@-node:rodrigob.20040123130224:split bar commands
    #@+node:rodrigob.20040122175312:menu commands
    #@+node:rodrigob.20040123133928:open
    def onOpen(self, event=None):
        """
        """
        
        from tkFileDialog import askopenfile
        
        t_file = askopenfile(mode="rw") # return the opened file
        
        if not t_file:
            self.log_error("Did not select a file to open.")
            
        else:
            pass
            # check if we have to save the current content
            if self.is_dirty(): # if file is dirty
                if self.filename: 
                    message = "File \"%s\" contains changes not yet saved to disk.\nDo you want to save the file before opening a new one ?" % self.filename
                else:
                    message = "The text has not been saved. Save before opening a new one ?"
    
                ret = self.askYesNoCancel("Save before opening", message) # ret 1, 0 or -1 for cancel
    
                if ret == 1:
                    # save the file
                    ret = self.onSave()
                    if not ret: # did not save
                        return # do not open
    
                elif ret == -1:
                    print "Open cancelled"
                    return
            
            # confirm disconnection desire (of ourself, and from everyone already connected to us)
            if self.node.connected:
                from tkMessageBox import askokcancel
                ret = askokcancel("Confirm disconnection",
                                  "You are connected to a remote server. Opening another file will close this connection. Proceed ?")
    
                if not ret:
                    print "Open cancelled"
                    return
                
                # disconnect ourself first
                self.node.disconnect_from_server()
                
            # open the file content
            base_text = None
            try:
                base_text = t_file.read()
            except IOError:
                print 'i/o error opening file %s, aborting' % t_file
    
            if not base_text:
                from tkMessageBox import showerror
                showerror('Error', 'Input/output error opening file %s, aborting.' % t_file)
                return
            
            # create a new ChalksNode instance
            self.node = ChalksNode(self, base_text)
            
            # update the window
            
        return
        
        
    #@-node:rodrigob.20040123133928:open
    #@+node:rodrigob.20040123140212:save
    def onSave(self, event=None):
        """
        Return true if saved, False else.
        """
        
        if self.file:
            # simply save the content
            self.save_text() # save the content
            
            self.log("saved: %s" % self.filename)
            ret = 1
        else:
            # ask for a filename
            from tkFileDialog import asksaveasfile
                    
            t_file = asksaveasfile(mode="rw") # return the file instance
            
            if not t_file:
                self.log_error("You did not selected a file to save as.")
                ret = 0
            else:
                
                # save the content
                self.save_text() 
                        
                from os.path import basename
                self.filename = basename(t_file.name)
                self.log("saved: %s" % self.filename)
                self.root.title("Chalks - %s" % self.filename)
                ret = 1
                
        return ret 
    #@+node:rodrigob.20040125211222:save text
    
    def save_text(self,):
        """
        Effectivelly flush the text to the local file.
        """
        
        assert hasattr(self, "file"), "No open file to save in"
        
        self.file.seek(0) # go back to the start
        text= self.text_widget.get("1.0", END)
        self.file.write(text)
        self.file.truncate() # mark the end of the file
        # we are done
        
        self.saved_version_hash = hash(text) # used to check later changes
        return
    #@-node:rodrigob.20040125211222:save text
    #@-node:rodrigob.20040123140212:save
    #@+node:rodrigob.20040123134358:connect to
    def onConnectTo(self, event=None):
        """
        Open the connect to dialog
        """
        top = Toplevel(self.root)
        top.title("Connect to ...")
        
        #|-|-|
        ttt_frame = LabelFrame(top, text="Available servers", padx=5, pady=5)
        self.server_listbox = Listbox(ttt_frame, width=46)    
        self.server_listbox.grid(row=0, column=0, pady=5)
    
        t_text = Label(ttt_frame, text="Select a server and enter a nickname to connect")
        t_text.grid(row=1, column=0)
        
        #|-|-|
        t_frame = LabelFrame(top, text="Enter remote server info", padx=5, pady=5)
        
        t_text = Label(t_frame, text="Address:")
        t_text.grid(row=0, column=0, pady=5)
    
        address_entry = t_entry = Entry(t_frame, width=16, background="white")
        t_entry.grid(row=0, column=1, sticky=W)
        t_entry.insert(END, "127.0.0.1")
            
        t_text = Label(t_frame, text="e.g. : 181.0.24.5")
        t_text.grid(row=1, column=0, columnspan=2, sticky=E)
    
        t_text = Label(t_frame, text="  Port:")
        t_text.grid(row=0, column=2)
    
        port_entry = t_entry = Entry(t_frame, width=5,  background="white")
        t_entry.grid(row=0, column=3, sticky=W)
        t_entry.insert(END, "8787")
        
        t_text = Label(t_frame, text="e.g. : 4321")
        t_text.grid(row=1, column=2, columnspan=2, sticky=E)
        
        #-|-|-
        tt_frame = LabelFrame(top, text="Identify yourself", padx=5, pady=5)
        
        t_text = Label(tt_frame, text="Nickname:")
        t_text.grid(row=2, column=0)
        
        nickname_entry = t_entry = Entry(tt_frame, width=8, background="white")
        t_entry.grid(row=2, column=1, sticky=W)
        t_username = guess_username() # guess the username
        t_entry.insert(END, t_username)
        
        # see binding below...
            
        t_text = Label(tt_frame, text="e.g. : mike")
        t_text.grid(row=3, column=0, columnspan=2, sticky=E)
        
        #-|-|-
        ttt_frame.pack(ipadx = 5)    
        t_frame.pack(ipadx = 5)
        tt_frame.pack(ipadx = 5)        
        #|-|-|
        
        t_frame = Frame(top)
        
        button_close = Button(t_frame, text="Close", command= top.destroy)
        button_close.pack(side=RIGHT, padx=10)
        
        from struct import unpack # used for unpacking IPv4 addresses from zeroconf
        
        #@    << server list callback >>
        #@+node:niederberger.20040911130819:<< server list callback >>
        def onServerListClick(event=None):
            if not self.server_listbox.curselection():
                return  # <<< tkinted only seems to consider entries as selected after clicking twice on a listbox
            
        #@+at 
        #@nonl
        # aargh, Tkinter is disgusting:
        # 1) curselection() returns STRINGS instead of ints when referring to 
        # indexes
        # 2) curselection() only returns something after you click TWICE on 
        # the list box. After that, it starts working as expected
        # 3) Listbox has no scrollbar, we have to set it up manually with:
        #     """
        #     frame = Frame(master)
        #     scrollbar = Scrollbar(frame, orient=VERTICAL)
        #     listbox = Listbox(frame, yscrollcommand=scrollbar.set)
        #     scrollbar.config(command=listbox.yview)
        #     scrollbar.pack(side=RIGHT, fill=Y)
        #     listbox.pack(side=LEFT, fill=BOTH, expand=1)
        #     """
        #@-at
        #@@c    
            server = self.cur_server_list[self.cur_server_list.keys()[int(self.server_listbox.curselection()[0])]]
            
            ipadr = '.'.join(map(lambda x:str(ord(x)),unpack('cccc', server['address'])))
            address_entry.delete(0, END); address_entry.insert(END, ipadr)
            port_entry.delete(0, END); port_entry.insert(END, str(server['port']))
            
        #@-node:niederberger.20040911130819:<< server list callback >>
        #@nl
        self.server_listbox.bind("<Button-1>", onServerListClick)
        
        #@    << connect to callback >>
        #@+node:rodrigob.20040125213003:<< connect to callback >>
        def connect_to_callback(event=None):
            """
            what happens when the "Connect to" button is pressed
            """
            # if required, request a save as 
            if self.is_dirty():
                if self.filename: 
                    message = "File \"%s\" contains changes not yet saved.\nOnce connected, a new text will be downloaded.\nDo you want to save the current file before connecting ?" % self.filename
                else:
                    message = "The text has not been saved.\nOnce connected, a new text will be downloaded.\nSave before connecting ?"
            
                ret = self.askYesNoCancel("Save and connect to ...", message) # ret 1, 0 or -1 for cancel
            
                if ret == 1:
                    # save the file
                    ret = self.onSave()
                    if not ret: # did not saved
                        return # do not quit
        
                elif ret == -1:
                    print "you canceled the connection process"
                    return
            
            port     = int(port_entry.get()) # connect_to_parent now expects an int as the port
            address  = address_entry.get()  
            nickname = nickname_entry.get()
            
            top.destroy() 
            # start the connection 
            self.node.connect_to_parent(address, port, nickname)
            return
        #@-node:rodrigob.20040125213003:<< connect to callback >>
        #@nl
        
        button_connect_to = Button(t_frame, text="Connect to", command=connect_to_callback, state=DISABLED, default=ACTIVE)
        button_connect_to.pack(side=RIGHT, padx=10)
        
        top.bind("<Return>", lambda e: button_connect_to["state"] == NORMAL and connect_to_callback() ) # call the command if the button is enabled
        
        #@    << validation callback>>
        #@+node:rodrigob.20040125213003.1:<< validation callback >>
        def validation_callback(event=None):
            """ simple callback that check every 200 ms if the filled data is valid"""
        
            port    = port_entry.get()
            address =  address_entry.get()  
            
            if address:
                title = "Connect to %s:%s" % (address, port)
            else:
                title = "Connect to ..."
            top.title(title)
            
            condition =  address and port.isdigit() and len(nickname_entry.get()) > 3
            
            if condition:
                button_connect_to.config(state=NORMAL)
            else:
                button_connect_to.config(state=DISABLED)
                
            button_connect_to.after(200, validation_callback) # call each 200 ms
            
            return
        #@-node:rodrigob.20040125213003.1:<< validation callback >>
        #@nl
            
        button_connect_to.after(200, validation_callback) # start ciclic calls each 200 ms
        
        t_frame.pack()    
        
        
        top.protocol("WM_DELETE_WINDOW", top.destroy)
    
        #@    << server monitor callback >>
        #@+node:niederberger.20040911120126:<< server monitor callback >>
        def server_monitor_callback(servers):    
            """
            this is called whenever the dict of known servers changes
            
            sample server data for reference:
                                        'address':     info.getAddress(),
                                      'identifier':  info.getName(),
                                      'port':       
            """        
            self.server_listbox.delete(0, END)  # remove all items
            self.cur_server_list = servers # set internal dict of current known servers. This is used later by the listbox callback to known which server the user clicked
            
            for server in servers.values(): # add all servers
                if server['identifier'] == self.service_name: # skip ourself
                    continue
                ipadr = '.'.join(map(lambda x:str(ord(x)),unpack('cccc', server['address'])))  # Ahhhhh ! Is this the best way for unpacking 4 bytes on a binary stream ?
                svr_string = server['identifier'] + ' [%s]' % ipadr
                print svr_string
                self.server_listbox.insert(END, svr_string)
        #@nonl
        #@-node:niederberger.20040911120126:<< server monitor callback >>
        #@nl
        
        if self.server_monitor:
            # register callback with serverMonitor object
            self.server_monitor.addCallbackListener(server_monitor_callback)
            # populate it for the first time
            server_monitor_callback(self.server_monitor.getServers())
        
        self.root.wait_window(top) # show
    
        if self.server_monitor:
            # unregister callback with serverMonitor object
            self.server_monitor.removeCallbackListener(server_monitor_callback)
        
        return
        
    #@nonl
    #@-node:rodrigob.20040123134358:connect to
    #@+node:rodrigob.20040913224357:disconnect
    def onDisconnect(self, event=None):
        """
        Disconnect dialog
        """
        
        from tkMessageBox import askokcancel
        ret = askokcancel("Confirm disconnection",
                          "You are connected to a remote server. Opening another file will close this connection. Proceed ?")
    
        if not ret:
            print "Disconnection cancelled"
            return
        else:
            print "Starting disconnection"           
            
        # disconnect ourself from the network
        self.node.disconnect_from_server()
        
        return
    #@-node:rodrigob.20040913224357:disconnect
    #@-node:rodrigob.20040122175312:menu commands
    #@+node:rodrigob.20040121153312:chat bar commands (onChatTextEntry)
    def onChattextEntry(self, event):
        """
        Obtain the last line in the text widget.
        Put the cursor at the end of the widget.
        Send the message.
        
        The event callback is called *before* that the key modify the text widget.
        """
        
        text = event.widget
    
        txt = text.get("insert linestart", "insert lineend")  # extract the actual line
        if len(txt) == 0: # return immediately on blank input text
            return
    
        # ensure that the cursor is on the last line, and that there is only one blank line at the end (new entry...)
        text.mark_set("insert", "end")	
        if text.get("insert - 1 chars") == '\n':
            text.delete("insert - 1 chars")
        
        if txt[0] == '/': # manage commands
            if txt.startswith("/presence"):
                t_list = txt.split(' ')
                if len(t_list) >= 2:
                    status = ' '.join(t_list[1:])
                    self.perspective.callRemote("set_presence", status)
                else:
                    self.log("Set your status online (dummy demo command by the moment).\ Example: '/presence happy coding'", color="gray")
                    
            elif txt.startswith("/help"):
                self.log("Actual defined commands are:\n'/help','/presence', (sorry, nothing else by now)", color="gray")
                
            else:
                cmd = txt.split(' ')[0]
                self.log_error("Unknown command '%s'; message not sent.\nUse '/help' to get some guidance."%(cmd))	
        else:
            t_from = self.node.nickname
            t_to = None # to everyone
            self.node.remote_send_message(self.node, t_from, t_to, txt)
        
        return
    
    
    #@+node:rodrigob.20040912221032:enable/disable Chat
    def enableChat(self):    
        """
        enables chat text entry widget
        """    
        self.chat_text_entry["state"] = NORMAL    
        self.chat_text_entry.delete('1.0', END);  
        #self.chat_text_entry.insert(END, "Enter chat text here");
        print "Chat bar now enabled"
        return
        
    def disableChat(self):    
        """
        disable chat text entry widget
        """    
        self.chat_text_entry.delete('1.0', END);  
        self.chat_text_entry.insert(END, "The chat bar is disabled until someone connects to you or you connect to someone.");
        self.chat_text_entry["state"] = DISABLED
        print "Chat bar now disabled"
        
        return
    #@nonl
    #@-node:rodrigob.20040912221032:enable/disable Chat
    #@-node:rodrigob.20040121153312:chat bar commands (onChatTextEntry)
    #@+node:rodrigob.20040124160427:status bar commands
    #@+node:rodrigob.20040121153834.4:updateStatusRowCol
    def updateStatusRowCol (self):
        
        row, col = tuple(map(int, self.text_widget.index(INSERT).split(".")))
        
        if self.node:
            t_string = "(row %3i, col %3i) (HB %3i, DOps %3i)" % (row, col, len(self.node.HB), len(self.node.delayed_operations))
        else:
            t_string = "(row %3i, col %3i)" % (row, col)
        
        self.rowcol_stringvar.set( t_string )
        
        self.status_bar.after(150, self.updateStatusRowCol)     # Reschedule this routine 150 ms. later.
        
    #@-node:rodrigob.20040121153834.4:updateStatusRowCol
    #@-node:rodrigob.20040124160427:status bar commands
    #@+node:rodrigob.20040123123802:help command
    # help is defined at the class level; to avoid leo identation problems
    #@<< chalks help >>
    #@+node:rodrigob.20040123132311.1:<< chalks help >>
    #@@color
    #@@language python
    # this is the documentation that will be seen by the end user, give a description of the panel and it's usage
    # this is part of the code, so do not delete the "help" definition and the """ elements.
    help = \
    """
    
    NOT YET WRITTEN
    
    #@+others
    #@+node:rodrigob.20040126020116:network graph (about Server, Client, Children, Parent, and Trees)
    #@+at
    # The network graph is a Tree.
    # The upper node is the first instance, that created the original content.
    # Down tree we found the other sessions.
    # Each node has one parent and possibly many childrens.
    #@-at
    #@@c
    #@nonl
    #@-node:rodrigob.20040126020116:network graph (about Server, Client, Children, Parent, and Trees)
    #@-others
    
    """
    
    #@-node:rodrigob.20040123132311.1:<< chalks help >>
    #@afterref
 # define 'help' (at the class level)
    
    def onHelp(self, event=None):
        """
        Show main help screen
        """
    
        from ScrolledText import ScrolledText
        top = Toplevel(self.root)
        top.title("Help")
        t = ScrolledText(top, wrap=WORD, padx=50); t.pack(expand=1, fill=BOTH)
        
        # add apropos
        t.insert(END, "\nChalks " + self.version + "\nLicensed under the GNU GPL\nCopyright 2004, Chalks Development Team")
        link_text = " Project homepage"
        t.insert(END, link_text)
        t.tag_config("hyperlink", underline=1, foreground="blue3")
        t.tag_bind("hyperlink", "<Button>", self.online_homepage)
        t.tag_add("hyperlink","end - %i chars" % (len(link_text) + 1), "end - 1 char")
        
        t.insert(END, "\n")
        t.insert(END, self.help) # insert the content
        t.config(state=DISABLED)
        Button(top, text="Close", command= top.destroy, default=ACTIVE).pack()
        top.protocol("WM_DELETE_WINDOW", top.destroy)
    
        self.root.wait_window(top) # show
        
        return
        
    #@+node:rodrigob.20040122173128:online_homepage
    
    def online_homepage(self, event=1):
        
        import webbrowser
    
        url = "http://chalks.berlios.de"
        
        try:
            webbrowser.open_new(url)
        except:
            print "not found: " + url
    #@-node:rodrigob.20040122173128:online_homepage
    #@-node:rodrigob.20040123123802:help command
    #@+node:rodrigob.20040913232538:set/clear connected
    # where to place this node ?
    
    def set_connected(self,):
        """
        Set the connected flag and conmute the asociated gui elements
        """
        
        # upon connection we need to enable the chat system 
        self.enableChat()
            
        # update the menu bar
        self.file_menu.entryconfig(1, label="Disconnect", command = self.onDisconnect)
        #file_menu.add_command(label="Connect to", underline=0, accelerator="Ctrl+T", command= self.onConnectTo)
        
        self.connected = 1
        return
        
    def clear_connected(self,):
        """
        Clear the connected flag and conmute the asociated gui elements
        """
        
        # upon connection we need to enable the chat system 
        self.disableChat()
                    
        # update the menu bar
        self.file_menu.entryconfig(1, label="Connect to", command = self.onConnectTo)
        #self.file_menu.entryconfig(1, label="Disconnect", command = self.onDisconnect)
        #file_menu.add_command(label="Connect to", underline=0, accelerator="Ctrl+T", command= self.onConnectTo)
        
        self.connected = 0
        return
    #@nonl
    #@-node:rodrigob.20040913232538:set/clear connected
    #@-node:rodrigob.20040123124005:gui commands/events
    #@-others
#@nonl
#@-node:rodrigob.20040119152542:class Chalks
#@+node:rodrigob.20040125154815.1:class ChalksNode
from ConcurrentEditable import ConcurrentEditableNode
from ConcurrentEditable import ConcurrentEditable # needed by remote_delete_text()

from twisted.internet.defer import DeferredList
        
class ChalksNode(ConcurrentEditableNode):
    """
    This is the local instance that take care of the collaborative edition and the network layers.
    This is the core object under the GUI.
    
    A Chalks node is part of a tree network, it can have one parent and N childrens.
    A node connect once to his parent and can receive N childrens connections.
    
    All messages that arrive to a node has to be repeated to the other nodes.
    This is the class that generate all the operations to be sent to the server, and it the the one that process the received operations.
    """

    #@    @+others
    #@+node:rodrigob.20041011002305:__init__
    def __init__(self, chalks_gui, text=""):
        """
        """
        
        ConcurrentEditableNode.__init__(self,)
    
        # initialize the extra attributes		
        self.chalks_gui  = chalks_gui # stores a reference to the gui object
    
        self.nickname = guess_username()
        self.connected = 0              # initially we are not connected to anyone
        
        # perspectives of the adjacent nodes in the network
        self.parent_perspective = None
        self.childrens_perspectives = []
        
        # attach some attributes and methods
        for t_name in ["log", "log_error", "exception", "encoding"]: 
            setattr(self, t_name, getattr(chalks_gui, t_name))
        self.log = lambda text, *args, **kws: chalks_gui.log("\n%s" % text) # dummy trick
                
        self.text_widget = chalks_gui.text_widget
        self.text_widget.tag_config("to_send", relief= RAISED, borderwidth=4, background= "beige")# work fine in Linux
            
        self.deletion_buffer = () # helper variable store a cumulative erasure (successive delete or insert commands) in the tuple (startpos, len)
    
        #<<<<< "text" parameter is not being used. Keep it in mind when fixing this method, as the open dialog will call it with textbase from a local file
        if text:
            self.set_text(text)        
    
        return
    
    
    #@-node:rodrigob.20041011002305:__init__
    #@+node:rodrigob.20040125154815.2:connect to/disconnect from parent node
    
    #@+others
    #@+node:rodrigob.20040913221730:connect to parent
    def connect_to_parent(self, address, port, nickname="No name"):
        """
        Connect as a children to a parent node
        This method overwrite the ConcurrentEditableNode implementation managing the network layer
        """
        print "Requesting a connection to 'chalks://%s:%s' as '%s', please wait..." % (address, port, nickname)
        
        assert isinstance(port, int), 'port must be integer'
        self.nickname = nickname    
        
        # we will give to the parent access to a local avatar
        parent_nickname = None
        parent_mind = None
        parent_avatar = ChalksAvatar(parent_nickname, parent_mind, self.chalks_gui)
        self.parent_avatar = parent_avatar
        
        factory = pb.PBClientFactory()
        reactor.connectTCP(address, port, factory)
        deferred = factory.login(credentials.UsernamePassword(nickname, "guest"), client=parent_avatar)
        deferred.addCallbacks(self.logged_in, self.exception)
    
        return
        
    def logged_in(self, avatar):
        """
        Start collaborating with the parent
        """
    
        self.avatar = avatar
        #our avatar is the our perspective to the parent ChalksNode
        self.parent_perspective = avatar
        self.parent_avatar.mind = avatar # set the avatar perspective (important)
        print "Registering parent perspective %s" % avatar 
    
            
        # we obtain our site_id
        #t_address = self.avatar.broker.transport.getHost()
        #self.site_id = hash("%s:%i" % (t_address.host, t_address.port))
        self.site_id = time.time() # seconds since the epoch
    
        deferred = self.avatar.callRemote("collaborate_in", self.site_id)
        deferred.addCallback(self.start_collaborating).addErrback(self.exception)
                                
        return
    
    #@+others
    #@+node:rodrigob.20040909060311:start collaborating
    def start_collaborating(self, ret_tuple):
        """
        Callback for the connection procedure.        
        """
    
        insert_index = self.text_widget.index("insert")
        
        assert len(ret_tuple) == 7, 'wrong number of state parameters received'
        """ What's returned by get_state():
        return  self.sites_index,
                self.state_vector_table,
                self.minimum_state_vector,
                self.HB,
                self.delayed_operations,
                self.text_buffer,
                self.state_vector
        """
        #site_index, num_of_sites, base_state_vector, base_text, ops_list = ret_tuple
        t_sites_index, t_state_vector_table, t_msv, t_HB, t_delayed_operations , base_text, base_state_vector = ret_tuple
    
        num_of_sites = len(t_sites_index)
    
        # init the internal ConcurrentEditable
        from ConcurrentEditable import ConcurrentEditable
        ConcurrentEditable.__init__(self, 1,2) # site_index, num_of_sites) # site_index, num_of_sites # the clients has site_index 1, thus state_vector == [server, client] # <<< This line seems fine, this should be managed in a different way by ConcurrentNode
    
        self.set_text(base_text)
    
        self.state_vector = base_state_vector # <<<< is this a correct idea ?
    
        self.log("Base state vector %s"% base_state_vector, color="yellow") # just for debugging
        self.log("Received ops_list (len == %s) %s"%( len(t_HB), t_HB), color="yellow") # just for debugging
        
        from ConcurrentEditable import Operation    
        for t_dict in t_HB: #ops_list is a list of dictionaries that define a list of operations
            self.receive_operation(Operation(**t_dict))	# instanciate and receive
        
        self.log("Setting the index mark back to his initial location: %s"% (insert_index),color="yellow")
        
        self.text_widget.mark_set("insert", insert_index) # try to keep the insert mark at the same place
        
        t_address = self.parent_perspective.broker.transport.getPeer()
        self.log("Connected to '%s:%i' as site '%s' (num_of_sites %s)"%(t_address.host, t_address.port, self.site_id, num_of_sites))
        
        self.log("HB after the connection %s"% self.HB, color="yellow") # just for debugging
        self.log("delayed_operations after the connection %s"% self.delayed_operations, color="yellow") # just for debugging
        self.log("self.state_vector %s" % self.state_vector, color="yellow") # just for debugging
    
    
        self.chalks_gui.set_connected() # set up the flag and reflect in the gui
        return
        
    #@-node:rodrigob.20040909060311:start collaborating
    #@-others
    #@nonl
    #@-node:rodrigob.20040913221730:connect to parent
    #@+node:rodrigob.20040913221730.1:disconnect
    def disconnect_from_server(self):
        """
        Disconnect from the server. Also warn all my children about my disconnection
        """    
        perspectives = self.childrens_perspectives + [self.parent_perspective]
        deferredList = []
        for t_perspective in perspectives:
            if not t_perspective: # skip Null perspective, probably my parent_perspective when I'm not connected to a parent
                continue
            t_deferred = t_perspective.callRemote("collaborate_out")
            t_deferred.addErrback(self.exception)
            deferredList.append(t_deferred)
    
        dl = DeferredList(deferredList)
        dl.addCallback(self.disconnected)
    
    def disconnected(self, *args):
        """
        Actions to be done by the ClientNode after his disconnection.
        """
    
        self.chalks_gui.clear_connected() # reflect in the gui the end of the connection
            
        # what should I do here ?, do I need to do something ?
        self.log("Disconnected from the old node.", color="gray") # just to do something
        
        return
    
    
    
    #@-node:rodrigob.20040913221730.1:disconnect
    #@-others
    
    
    
    
    
    
    
    #@-node:rodrigob.20040125154815.2:connect to/disconnect from parent node
    #@+node:rodrigob.20040912225813:add/del sites
    #@+at
    # Register/Unregister childrens in the session
    #@-at
    #@nonl
    #@+node:rodrigob.20040912225813.1:add site
    def add_site(self, site_perspective):
        """
        Add a new children to the local node
        """
        
        if not self.connected:
            self.chalks_gui.set_connected()
            
        
        print "User %s %s is starting to collaborate" % (site_perspective.nickname, site_perspective)
        self.childrens_perspectives.append(site_perspective)
        ConcurrentEditableNode.add_site(self, site_perspective.site_id)
        
        return
        
    #@nonl
    #@-node:rodrigob.20040912225813.1:add site
    #@+node:rodrigob.20040912225813.2:del site
    def del_site(self, site_perspective):
        """
        Delete a children from the local node
        """
    
        print "User %s %s is quiting" % (site_perspective.nickname, site_perspective.mind)
        self.childrens_perspectives.remove(site_perspective)
        ConcurrentEditableNode.add_site(self, site_perspective.site_id)
        
        if not self.childrens_perspectives and not self.parent_perspective:
            self.connected = 0 
            self.chalks_gui.disableChat()
        return
        
    #@nonl
    #@-node:rodrigob.20040912225813.2:del site
    #@-node:rodrigob.20040912225813:add/del sites
    #@+node:rodrigob.20040125154815.3:edit content
    #@+at
    # This methods edit the client node text, presenting the gui results.
    # Essentially this method take care of allowing the user to input text 
    # while receiving operations and solve the unicode inconsistencies between 
    # Tkinter and the python string manipulation.
    # 
    # Unmanaged text in the text_widget is marked as "to_send".
    #@-at
    #@@c
    
    
    def set_cursor_position(self, who, pos):
        """ 
        Define the new position of someone cursor, so the local user can suspect future editions of the camarades. Used as a visual feedback of other user actions.
        """
        
        raise NotImplementedError, "not yet implemented"
        
        return
    #@nonl
    #@+node:rodrigob.20040125154815.4:set text
    def set_text(self, new_text):
        """
        Blindly overwrite the text of this site. (including the "to_send" elements)
        """    
        self.log( "Calling set_text '%s'"%(new_text), color="yellow" ) # for debugging
        
        # maintain an unicode buffer equivalent
        ConcurrentEditableNode.set_text(self, new_text)
                
        # clean up the body
        self.text_widget.delete("1.0", END)
        
        # insert the new text
        self.insert_text(0, new_text, op={"source_site":self.site_index})
        
        return
    
    
    
    #@-node:rodrigob.20040125154815.4:set text
    #@+node:rodrigob.20040125154815.5:insert text
    def insert_text(self, startpos, text, op={}):
        """ 
        Some one insert text on the actual node.
        Should insert text only counting non "to_send" locations.
        """
        
        if op.get("avoid"):
            self.log( "AutoInsertion is avoiyed", color="yellow") # for debugging
            del op["avoid"] # I hope this will edit the operation stored in the HB
            self.log("HB after operation avoyance %s"% self.HB, color="yellow") # just for debugging
            return
    
            
        text_widget = self.text_widget
            
        t_startpos = startpos
    
        # convert the insertion point, considering the "to_send" elements
        ranges = text_widget.tag_ranges("to_send") # ranges are text indexes
        
        for i in xrange(0, len(ranges), 2):
            # convert text indexes to numerical values
            start =          len(text_widget.get("1.0",     ranges[i]  ))
            stop  =  start + len(text_widget.get(ranges[i], ranges[i+1]))
            
            if start < startpos:
                startpos += stop - start # make the startpos include the unsent local text.
            if start >= startpos:
                break
            # else: continue
    
        startpos = "1.0 + %i chars"%(startpos)
                    
        self.log("Insert text: input starpos %s, real startpos %s. to_send ranges %s"%(t_startpos, startpos, ranges), color="yellow")
        
        # now startpos is a "line.column" index that consider the correct location
                
                
        if op["source_site"] == self.site_index: # if it is a confirmation
            who = None
        else:
            who = op.get("who")
        
        if who and who != self.name:
                
            # check if the who tag exists
            if who not in text_widget.tag_names(): # this is slowww <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< (how to do it fast?)
                # find a new color (fixed saturation and value. tint is random)(this ensure us to have only 'pleasant' background colors)						
                r,b,g = map(lambda x: int(x*255), colorsys.hsv_to_rgb( random.Random().random(), 
                                                                        0.30 , # thee important value (0 white, 1.0 intense color)
                                                                        1.0
                                                                      ))			
                t_color = "#%02x%02x%02x"%(r,g,b)
                
                text_widget.tag_config(who, background = t_color)
                text_widget.tag_bind(who, "<Button-1>", lambda event: self.log("Text inserted by %s"%(who), color=t_color))
            # end of new tag
            
            text_widget.insert(startpos, text, who)
            
        else: # no 'who', just insert the text
        
            text_widget.insert(startpos, text)
        
        self.log( "%s insert at %s the content '%s'"%(who, startpos, text), color="yellow" ) # for debugging
        
        return
    
    #@-node:rodrigob.20040125154815.5:insert text
    #@+node:rodrigob.20040125154815.6:delete text
    def delete_text(self, startpos, length, op={}):
        """ 
        Some one delete text on the actual node.
        Should delete text in  non "to_send" locations.
        Delete only remote solicitations, local text was already deleted.
        """
    
        if op.get("avoid"):
            self.log( "AutoDeletion is avoiyed", color="yellow") # for debugging
            del op["avoid"] # I hope this will edit the operation stored in the HB
            self.log("HB after operation avoidance %s"% self.HB, color="yellow") # just for debugging
    
            return
    
    
        text_widget = self.text_widget
        
        # convert the starting and end points, considering the "to_send" elements
        ranges = text_widget.tag_ranges("to_send") # return a list of index tuples
        
        for i in xrange(0, len(ranges), 2):
            # convert text indexes to numerical values
            start =          len(text_widget.get("1.0",     ranges[i]  ))
            stop  =  start + len(text_widget.get(ranges[i], ranges[i+1]))
            
            if start < startpos:
                startpos += (stop - start) # make the startpos include the unsent local text.
                
            if start >= startpos:
                ranges = ranges[i:] # store the rest (including actual pos)
                break
            # else: continue
            
                        
        self.log( "Deleting text at %s len %s"%(startpos, length), color="yellow" ) # for debugging
        
        # delete the text avoiying the "to_send" elements. 
        deleted_text = ""
        offset = 0
        for i in xrange(0, len(ranges), 2): #ranges contain the indexes of the rest of the "to_send" elements
            # convert text indexes to numerical values
            range_start =                len(text_widget.get("1.0", "%s - %i chars"%(ranges[i], offset)  ))
            range_stop  =  range_start + len(text_widget.get( "%s - %i chars"%(ranges[i], offset), "%s - %i chars"%(ranges[i+1], offset))) 
            
            if startpos + length >= range_start: # there is an overlapping
                            
                t_start = "1.0 + %i chars"%(startpos)
                t_stop  = "1.0 + %i chars"%(range_start)
    
                deleted_text += text_widget.get(t_start, t_stop)  # necessary for algorithm internal undo/redo	operations
                text_widget.delete(t_start, t_stop)
                
                length  -= range_start - startpos
                offset  += range_start - startpos
                startpos = range_stop - (range_start - startpos) # <<<<<<<<< this line is wrong
                # continue
                self.log( "continuing deletion at %s len %s"%(startpos, length), color="yellow" ) # for debugging
            else:
                break
            # end of for
    
        # the last one is direct (or the only one if no ranges==[])
        if length > 0:
            t_start = "1.0 + %i chars"%(startpos)
            t_stop  = "1.0 + %i chars"%(startpos + length)
    
            deleted_text += text_widget.get(t_start, t_stop)  # necessary for algorithm internal undo/redo	operations
            text_widget.delete(t_start, t_stop)
        #end of last deletion
        
        # keep the deleted text for future operation undo
        op["deleted_text"] = deleted_text
        
        return
        
    #@-node:rodrigob.20040125154815.6:delete text
    #@+node:rodrigob.20040125154815.8:fill body
    def fill_body(self, keywords):
        """
        Process each new key received in the body.
        Attached to OnBodyKey2 (well, really on idle_on_body_key). All params are passed as a keyword.
        Manage insertions, deletions, suppresions, range text overwrite and paste operations.
        
        Note that OnBodyKey2 is called for evey key, but not necesarrely inmediatelly after the key was pressed. The TextWidget contents can have changed since.
            
        fill_body has to mark the to_send chars and trigger the proper delete_text calls.
        This function is associated to the flush_body method, that will check the to_send chars, and send them when proper.
        """
        
        ch = keywords["ch"]
        old_sel    = keywords["oldSel"] # (first, last)
        old_text   = keywords["oldText"] or ""
        undo_type  = keywords["undoType"]
        old_insert = old_sel[0]
        old_tags_ranges    = keywords["oldTagsRanges"]	
        old_to_send_ranges = old_tags_ranges.get("to_send")
    
        #self.log("fill_body keywords %s"%(keywords), color="yellow") # just for debugging
        #trace("onbodykey2 keywords %s"%(keywords)) # just for debugging
    
    
        # some local helpers functions	
        #@    << def index_to_list>>
        #@+middle:rodrigob.20040125154815.9:helpers functions
        #@+node:rodrigob.20040125154815.10:<< def index_to_list >>
        def index_to_list(val):
            """
            Convert a Tkinter string index to a list of two integer elements [line, column].
            """
            if type(val) is str:
                return map(int, val.split("."))
            else:
                return val
            
        def list_to_index(val):
            """
            Convert [line, column] list to a Tkinter index.
            """
            return "%i.%i"%tuple(val)
        #@nonl
        #@-node:rodrigob.20040125154815.10:<< def index_to_list >>
        #@-middle:rodrigob.20040125154815.9:helpers functions
        #@nl
        #@    << def in_range>>
        #@+middle:rodrigob.20040125154815.9:helpers functions
        #@+node:rodrigob.20040125154815.11:<< def in_range >>
        def in_range(index, ranges):
            """
            return true if the index is in the range. false else.
            the true value returned is the (start, end) tuple corresponding to the range that covers the indicated index.
            """
            
            index =  index_to_list(index)
            
            for i in xrange(0, len(ranges), 2):	
                start  = index_to_list(ranges[i])
                stop   = index_to_list(ranges[i+1])
        
                if start <= index and index <= stop:
                    return list_to_index(start), list_to_index(stop)
                else:
                    continue
        
            return None # did not found the index in a range
        
        #@-node:rodrigob.20040125154815.11:<< def in_range >>
        #@-middle:rodrigob.20040125154815.9:helpers functions
        #@nl
        #@    << def range_to_pos_and_length >>
        #@+middle:rodrigob.20040125154815.9:helpers functions
        #@+node:rodrigob.20040125154815.12:<< def range_to_pos_and_length >>
        def range_to_pos_and_length(start, stop, text):
            """
            Convert a Tkinter range to a (length, position) index (used for the Operations definition).
            """
                
            start = index_to_list(start)
            stop  = index_to_list(stop)
            
            assert text, "The text parameter is %s, this argument is indispensable." % text
                
            if type(text) is unicode:
                text = text.split("\n")
            
            assert type(text[0]) is unicode, "Text data has to be unicode, to be comparable with the tkinter indexes."
            
            # Tkinter count the lines from 1 to N and the columns from zero to N
            
            pos    = start[1] + reduce(lambda x,y: len(y) + x, text[:start[0]-1], 0) + (start[0]-1) # columns + rows length + "\n" chars
            length = stop [1] - start[1] + reduce(lambda x,y: len(y) + x, text[start[0]-1:stop[0]-1], 0) + (stop[0] - start[0]) # stop columns - start columns + rows length + "\n" chars
            
            #print "\nrange_to_pos_length(start=%s, stop=%s, some_text) => pos, length == %s, %s"%( start, stop, pos, length) # just for debugging
            
            return pos, length
        #@-node:rodrigob.20040125154815.12:<< def range_to_pos_and_length >>
        #@-middle:rodrigob.20040125154815.9:helpers functions
        #@nl
        
        if old_sel and old_sel[0] != old_sel[1] and ch: # text was overwritten	(pressed a key while having a non void selection)
            #@        << text was overwritten >>
            #@+node:rodrigob.20040125154815.13:<< text was overwritten >>
            # (should check which overwritten text was already sent)
            # and should create a sequence of deletion operations
            
            self.log("text was overwritten %s;"%(old_sel), color="yellow")
            
            # need to define the lists:
            #	- text_deletion_ranges
            #   - to_send_deletion_ranges
            
            # has as input:
            #   - old_to_send_ranges
            #   - old_sel
            #   - old_text
                
            #print "old_sel", old_sel
            #print "old_to_send_ranges", old_to_send_ranges
            
            old_sel =	map(index_to_list, old_sel)
            ranges =	old_to_send_ranges
            t_ranges = [] # will keep the list of to_send ranges that are embedded in the old_sel range.
            
            # first we prune the to_send_ranges to get only the ranges of interest
            if not ranges:
                ranges=[]
            i = 0 # if ranges is []
            for i in xrange(0, len(ranges), 2):	
                start  = index_to_list(ranges[i])
                stop   = index_to_list(ranges[i+1])
                # search the initial range
                
                if start >= old_sel[0]: # found the initial range
                    break # lets continue with a new logic
                elif  stop >= old_sel[0]:
                    t_ranges.append(old_sel[0])
                    t_ranges.append(min(stop, old_sel[1]))
                    i += 2
                    break
                else:
                    continue
            
            for i in xrange(i, len(ranges), 2):	# starting from last point
                start  = index_to_list(ranges[i])
                stop   = index_to_list(ranges[i+1])	
                
                if start <= old_sel[1]: 
                    t_ranges.append(start)
                else:
                    break # job finished
                    
                if stop <= old_sel[1]:
                    t_ranges.append(stop)
                else:
                    t_ranges.append(old_sel[1])
                    break # job finished
                
            # now we convert the data to lineal ranges and check the valid deletion ranges	
            ranges = to_send_deletion_ranges = t_ranges
            #print "to_send_deletion_ranges", to_send_deletion_ranges
            ranges.insert(0, old_sel[0])
            ranges.append(old_sel[1])
            t_ranges = []
            for i in xrange(0, len(ranges), 2):	
                t_ranges.append( range_to_pos_and_length(ranges[i], ranges[i+1], old_text) )
            
            ranges   = t_ranges
            t_ranges = []
            t_ranges = filter(lambda x: x[1] > 0, ranges) # if length > 0, keep it
            
            text_deletion_ranges = t_ranges # text_deletion_ranges is a list of (pos, length) tuples that indicates the text areas that where deleted.
            self.log( "text_deletion_ranges %s"%text_deletion_ranges, color="yellow") # just for debugging
            
            # send the deletion operations
            for pos, length in text_deletion_ranges:
                deferred = self.send_operation("delete_text", pos, length)
                
            # mark the overwriter char					
            if ch not in ['\x7f', '\x08']:
                self.text_widget.tag_add("to_send",  old_insert)		
            #@-node:rodrigob.20040125154815.13:<< text was overwritten >>
            #@nl
        elif ch in ['\x7f', '\x08']: 
            #@        << suppression or deletion >>
            #@+node:rodrigob.20040125154815.14:<< suppression or deletion >>
            # suppression or deletion 
            # if the operation was applied in a to_send char, we omit it,
            # else we add it to the deletion buffer, that will be latter send over the network.
            # the idea is: we sum any deletion operation until any other key is pressed, then we send it.
            
            has_to_delete = None
            ranges = old_to_send_ranges
            if ch == '\x7f': #key Suppr, a suppression
                t_index = old_insert
                t_range = in_range(t_index, ranges) # return the range which touch the index
                if t_range and t_index != t_range[1]:
                    self.log("supressed a to_send char", color="yellow")
                    # nothing more to do
                    has_to_delete = None
                else: 
                    # suppressed text
                    delta = 0
                    has_to_delete = 1
                    
            elif ch == '\x08': #key, '\x08' # delete, a deletion
                t_index = old_insert
                t_range = in_range(t_index, ranges) # return the range which touch the index
                if t_range and t_index != t_range[0]:
                    self.log("deleted a to_send char", color="yellow")
                    # nothing more to do
                    has_to_delete = None
                else: 
                    # deleted text
                    delta = -1
                    has_to_delete = 1
            
            
            if has_to_delete:
                # at his point the deletion was efectued over a non to_send char, and it need to be registered in the deletion buffer.
                # we register sequences of deletion or suppr key, if the user press any other key, deletion_buffer will be flushed by flush body. If the deletion_buffer was not flushed that means that the last key that was pressed is a deletion or suppression key.
                
                if self.deletion_buffer: # updating a deletion buffer
                    #@        << update the deletion buffer >>
                    #@+node:rodrigob.20040125154815.15:<< update the deletion buffer >>
                    startpos, t_len = self.deletion_buffer
                    startpos += delta				
                    t_len += 1
                    self.deletion_buffer = (startpos, t_len)
                    
                    #self.log("fill body: updated the deletion buffer [startpos, len] == %s" % ([startpos, t_len]), color="yellow" ) # just for debugging
                    #@nonl
                    #@-node:rodrigob.20040125154815.15:<< update the deletion buffer >>
                    #@nl
                else: # need to create a new deletion buffer
                    #@        << create a new deletion buffer >>
                    #@+node:rodrigob.20040125154815.16:<< create a new deletion buffer >>
                    # obtain the startpos; omiting the old_to_send ranges
                    
                    old_insert = index_to_list(old_insert)
                        
                    if t_range: # if the old_insert touch a range
                        # t_range store the range that touch our index. We know that the ranges are ordered from little to bigger. So we cut the old_to_send_ranges list (but including the touching range).		
                        # convert the tuple of "line.column" indexes to a list of indexes.
                        iter_ranges = iter(ranges)
                        ranges= []
                        for t_index in iter_ranges:
                            ranges.append((t_index, iter_ranges.next()))
                        ranges = ranges[:ranges.index(index_to_list(t_range)) + 1]
                    else:
                        # we gonna have to search the ranges, knowing that they do not touch our index
                        t_ranges = []
                        for i in xrange(0, len(ranges), 2):	
                            stop   = index_to_list(ranges[i+1])
                            if old_insert > stop:
                                start  = index_to_list(ranges[i])
                                t_ranges.append((start, stop))
                                
                        ranges = t_ranges
                        
                    # now we have the list of "to_send" ranges that are found in the range ["1.0", "insert"]
                    
                    # we convert it to a [(pos, length), (pos, length), ...] form
                    old_text = old_text.split("\n")
                    t_ranges = []
                    for t_range in ranges:	
                        t_ranges.append( range_to_pos_and_length(t_range[0], t_range[1], old_text) )
                    
                    # we obtain the linear startpos
                    t_startpos  = old_insert[1] + reduce(lambda x,y: len(y) + x, old_text[:old_insert[0]-1], 0) + (old_insert[0]-1) # columns + rows length + "\n" chars
                    
                    
                    # and finally we obtain the real startpos by eliminating the to_send ranges.
                    startpos = t_startpos
                    for pos, length in t_ranges:
                        if pos < t_startpos:
                            startpos -= min(length, t_startpos - pos)
                    
                    # so we create the deletion_buffer !		
                    startpos += delta				
                    t_len = 1
                    self.deletion_buffer = (startpos, t_len)
                    
                    #self.log("fill body: created a new deletion buffer [startpos, len] == %s"%([startpos, t_len]), color="yellow" ) # just for debugging
                    #@-node:rodrigob.20040125154815.16:<< create a new deletion buffer >>
                    #@nl
            #@-node:rodrigob.20040125154815.14:<< suppression or deletion >>
            #@nl
        elif undo_type == "Typing" and ch: 
            #@        << "normal" keys>>
            #@+node:rodrigob.20040125154815.17:<< "normal" keys >>
            # a 'normal' key was typed
            # the flush command is called for every key OnBodyKey1
            # the flush command check the deletion buffer and flush it as necessary
                                
            for tag in self.text_widget.tag_names(): #clean up any other tag
                if tag not in ["sel", "to_send"]:
                    self.text_widget.tag_remove(tag, old_insert)
                    
            # mark the actual chars					
            self.text_widget.tag_add("to_send",  old_insert)		
            
            #self.log("%s"%(ch), color="yellow") # just for debugging
            #@-node:rodrigob.20040125154815.17:<< "normal" keys >>
            #@nl
        elif undo_type == "Paste":
            #@        << text paste >>
            #@+node:rodrigob.20040125154815.18:<< text paste >>
            
            
            # some text was pasted in the body
                    
            # get the old_star and old_end indexes
            
            old_paste_start  = keywords["oldSel"][0]
            old_paste_stop   = keywords["newSel"][0]
            
            # mark the inserted chars					
            self.text_widget.tag_add("to_send",  old_paste_start, old_paste_stop)		
            
            
            # tadaa!
            #@nonl
            #@-node:rodrigob.20040125154815.18:<< text paste >>
            #@nl
        else: 
            # non text insertion keys (move arrow, page up, etc...)
            pass
            #if ch and len(ch) > 0: self.log("unmanaged key %c" % ch, color="yellow") # just for debugging
            #self.log("unmanaged key of type %s"%(undo_type), color="yellow") # just for debugging
            
                
        self.flush_body(keywords) # send the unsent data and clean up what is necesarry.
        
        return
    #@nonl
    #@+node:rodrigob.20040125154815.9:helpers functions
    #@-node:rodrigob.20040125154815.9:helpers functions
    #@-node:rodrigob.20040125154815.8:fill body
    #@+node:rodrigob.20040125154815.19:flush body <<< BUG HERE ??
    def flush_body(self, keywords={}, all=0):
        """
        Send all the "to_send" that acomplish the criteria, send the operation related to the deletion buffer if necessary.
        This is the function that normally generate the operations to be sent (sometimes fill_body create some of them).
        This function is called at the end of fill_body and by idle_body_key if the user press non editing keys.
        """
        
        #self.log("flush_body: being called", color="yellow") # just for debugging
                    
        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EDIT THIS CODE should include a deferred.timeout operation that calls flush(all)<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    
        # <<<<<<<<<<<<<<<<<<<<<<<<<<< end of experimental code
    
        undo_type       = keywords.get("undoType")
        ch              = keywords.get("ch")
        
        if self.deletion_buffer:
            if ((undo_type == "Typing" and ch not in ['\x7f', '\x08']) or all):  # at the end of a chunk deletion, that is, the user was deleting (using delete or suppr) but now he has pressed any other key, so we have to send the operation.
            
                # flush the deletion buffer
                deferred = self.send_operation("delete_text", self.deletion_buffer[0], self.deletion_buffer[1]) # <<< send or receive operation ?
                
                self.log("deletion_buffer executed with value (%i %i)"%(self.deletion_buffer[0], self.deletion_buffer[1]), color="yellow") # just for debugging
                                
                self.deletion_buffer = ()	
        
            
    
        # flush the insertions
        text = self.text_widget
        #ranges = old_tags_ranges
        # flush body does not require to care about the past, only about the present.
        ranges = self.text_widget.tag_ranges("to_send")
        insert_index= "insert"
        
        for i in xrange(0, len(ranges), 2):	
            start  = ranges[i]
            stop   = ranges[i+1]
            t_text = None 
    
            # self.log("(%s,%s)"%(start, stop), color="yellow") # for debugging
                    
            # conditions for text flushing -~-~-~-~-~-~-~-~-~-~
            tt_text = text.get("%s - 2 chars"%(stop), stop)
            
            if len(tt_text) == 2 and tt_text[1] in [' ', '\n'] and tt_text[0] != tt_text[1]: # when the user finish a word and insert a space or an enter.
                t_text = text.get(start, stop)		
    
            elif (		text.compare(insert_index, "<", "%s - 5  chars"%(start)) 
                or  text.compare(insert_index, ">", "%s + 5  chars"%(stop) ) ): # if we are 5 chars away from a chunk
                t_text = text.get(start, stop)
                
            elif (   text.compare(insert_index, ">", "%s + 1 lines"%(stop) )
                  or text.compare(insert_index, "<", "%s - 1 lines"%(start)) ) : # if we are 1 lines away from a chunk
                t_text = text.get(start, stop)
    
            elif (   text.compare(stop,   ">", "%s + 2 lines"%(start) )
                  or text.compare(stop,   ">", "%s + 30 chars"%(start)) ) : # if the chunk has more than 2 lines or is bigger than 30 chars.
                t_text = text.get(start, stop)
    
                
            elif all: # if we have to flush every dirty char
                t_text = text.get(start, stop)
                
            # check if the conditions trigered some text flushing  -~-~-~-~-~-~-~-~-~-~
    
        
            if t_text:
                #self.log(t_text, color="orange") # for debugging
                #self.log("flush_body, flushing the range (%s,%s)"%(start, stop), color="yellow") # for debugging
                
                # transform the start index to a lineal index
                startpos = len(text.get("1.0", start))
                
                # remove the tags
                text.tag_remove("to_send", start, stop)
                
                # send the data
                self.send_operation("insert_text", startpos, t_text) # <<< send or receive operation ?
                
        return
    #@-node:rodrigob.20040125154815.19:flush body <<< BUG HERE ??
    #@-node:rodrigob.20040125154815.3:edit content
    #@+node:rodrigob.20041014201949:network aware methods
    #@+node:rodrigob.20040125154815.7:send operation <<< BUG HERE
    def send_operation(self, site_perspective, t_op):
        """
        Implement the network layer that allow sending operation to a remote reference
        """
        
        site_perspective.callRemote("receive_op", t_op["type"], t_op["pos"], t_op["data"], t_op["timestamp"]).addErrback(self.exception)
                
        return
    
    
    #@+node:rodrigob.20041014201949.1:old
    
    def send_operation(self, op_type, pos, data): # <<< Should be def send_operation(self, site_index, t_op):
        """
        Apply locally and then send the operation to all the adjacent nodes (upward and downward the tree).
        This method overwrite the ConcurrentEditableNode implementation to take care of the network layer.
        """
        
        if op_type == "insert_text":
            op_type = "Insert"
            # convert data to unicode
            data = unicode(data, self.encoding, "strict")
    
        elif op_type == "delete_text":
            op_type = "Delete"
            
        else:
            raise "Unknown op_type '%s'"%op_type
        
        # apply locally
        self.gen_op(op_type, pos, data, avoid=1) # will avoid the effects the first time.
    
        
        # convert the state vector to a dict representation
        state_vector = {}
        for site_id, pos in self.sites_index.items():
            state_vector[site_id] = self.state_vector[pos]
        
    
        # send to all the connected sites
        perspectives = self.childrens_perspectives + [self.parent_perspective]
        for perspective in perspectives:
            if perspective:       
                # send to the other nodes
                perspective.callRemote("receive_op", op_type, pos, data, state_vector).addErrback(self.exception)
        
        return
    
    #@-node:rodrigob.20041014201949.1:old
    #@-node:rodrigob.20040125154815.7:send operation <<< BUG HERE
    #@+node:rodrigob.20040127182438:remote callable methods
    #@+at
    # This are the method the Avatars are suposed to access. This are the only 
    # method that other nodes should be able to call.
    # 
    # The ChalksAvatar implementation have to be consistent with this 
    # ChalksNode methods.
    #@-at
    #@@c
    #@nonl
    #@+node:rodrigob.20040127184605:send message
    def remote_send_message(self, received_from, from_, to, txt):
        """ 
        received_from: perspective that gave to us the message
        from: string, nickname of the emitter
        to: string, nickname of the receiver
        txt: the message
        
        A remote node send a message to us
        we repeat it to every known node except from the one that gived the message to us
        if to is None, the message will be spread to all, else it will be sent only to the users named like to
        """
    
    
        if (not to) or (to == self.nickname):    
            self.log("<%s> %s" %(from_, txt) )
        
        
        perspectives = self.childrens_perspectives + [self.parent_perspective]
    
    #@+at        
    #     # diagnose code
    #     #print "<%s> %s" %(from_, txt)
    #     print "received_from %s" % received_from
    #     #print "perspectives %s" % perspectives
    #     print "[x==%s for x in %s] == %s" %(received_from, perspectives, 
    # [x==received_from for x in perspectives])
    #@-at
    #@@c
    #@+at
    #     if self.parent_perspective: 
    # self.parent_perspective.callRemote("send_message", from_, to, 
    # txt).addErrback(lambda _, name: self.log_error("Could not send the 
    # message from user %s to user %s"), from_, to)
    #     return # to avoid horrible loop
    #@-at
    #@@c
        
        for t_perspective in perspectives:
            if t_perspective and received_from != t_perspective:
                #print "%s.callRemote('send_message', ..." % t_perspective
                t_deferred = t_perspective.callRemote("send_message", from_, to, txt)
                t_deferred.addErrback(lambda _, name: self.log_error("Could not send the message from user %s to user %s"), from_, to)
        #print
        
        return
    #@-node:rodrigob.20040127184605:send message
    #@+node:rodrigob.20040920122333:receive operation
    def remote_receive_operation(self, received_from, in_op, *args, **kw):
        """
        Receive an operation from a remote location
        """
    
        from ConcurrentEditable import Operation # this line should not be at the begining of Chalks.py ?
        
        # obtain the input operation
        if not isinstance(in_op, Operation):
            try:
                assert len(args) >= 2
                t_op = Operation(in_op, args[0], args[1])
                for k in kw:
                    t_op[k] = kw[k]
            except:
                raise "Error on receive_operation arguments (%s, %s, %s)"%(in_op, args, kw)
        else:
            t_op =	Operation(**in_op) # copy the operation 
            
        if dbg >=1:
            print "Node applying op %s"%(t_op)
        
        # ---
        
        ConcurrentEditableNode.receive_operation(self, t_op) # apply localy
        # ---
        
        
        perspectives = self.childrens_perspectives + [self.parent_perspective]
    
    #@+at        
    #     # diagnose code
    #     #print "%s" %(t_op)
    #     print "received_from %s" % received_from
    #     #print "perspectives %s" % perspectives
    #     print "[x==%s for x in %s] == %s" %(received_from, perspectives, 
    # [x==received_from for x in perspectives])
    #@-at
    #@@c
    #@+at
    #     if self.parent_perspective: 
    # self.parent_perspective.callRemote("send_message", from_, to, 
    # txt).addErrback(lambda _, name: self.log_error("Could not send the 
    # message from user %s to user %s"), from_, to)
    #     return # to avoid horrible loop
    #@-at
    #@@c
        
        for t_perspective in perspectives:
            if t_perspective and received_from != t_perspective:
                #print "%s.callRemote('send_message', ..." % t_perspective
                t_deferred = t_perspective.callRemote("receive_operation", in_op, *args, **kw)
                t_deferred.addErrback(lambda _, name: self.log_error("Could not send the message from user %s to user %s"), from_, to)
        #print
        
        
        return
    
    remote_receive_op = remote_receive_operation # alias
    receive_operation = remote_receive_operation # alias
    receive_op = receive_operation # alias
    #@-node:rodrigob.20040920122333:receive operation
    #@-node:rodrigob.20040127182438:remote callable methods
    #@-node:rodrigob.20041014201949:network aware methods
    #@-others
#@nonl
#@-node:rodrigob.20040125154815.1:class ChalksNode
#@+node:rodrigob.20040125194534:class ChalksAvatar
class ChalksAvatar(pb.Avatar, pb.Referenceable):
    """
    <<<<<<< ADD CONTENT HERE
    what other users (childrens) can do here (at the parent). 
    The avatar instance is created when the user connects to the local node, and it defines what he can do here.
    
    The server side representation of the user.
    There is one avatar instance per client connection to the server
    """
    
    def __init__(self, avatarId, mind, chalks_gui = None):
        """
        """
        
        assert chalks_gui
        self.chalks_gui = chalks_gui
        self.node = chalks_gui.node
        
        self.mind = mind # store it for later use # mind is a perspective of the client that is connecting to use
        self.avatarId = self.nickname = avatarId
        if self.mind: self.mind.nickname = avatarId
            
        # this assertion has to be relaxed to enable childrens side avatar creations
        #assert mind, ChalksError("Chalks strictly require references to the client connecting.")
    
        #if mind: assert type(mind) is pb.Reference # if mind assert it is a remote reference
        
        #pb.Avatar.__init__(self, avatarId, mind) # pb.Avatar has no __init__ method.
        

        # copy every perspective_ method in remote_ method
        perspective_methods = ['_'.join(x.split('_')[1:]) for x in dir(self) if x.split('_')[0] == "perspective"] # ugly hack
        #print "Avatar perspective_methods", perspective_methods
        for t_name in perspective_methods:
            if t_name:
                setattr(self, "remote_"+t_name, getattr(self, "perspective_"+t_name))
                #print "Added method %s to ChalksAvatar class"%("remote_"+t_name)


        return
        
    #@    @+others
    #@+node:rodrigob.20040126020641:collaborate in/out
    # Allow external users to start collaborating
    def perspective_collaborate_in(self, site_id):
        """
        Start collaborating with the node
        proceeds with site registration and returns the necessary data to configure the client (children)
        the site_id is a unique identifier of the client (child) process
        """
            
        self.site_id = site_id
        if self.mind: self.mind.site_id = site_id
        
        assert self.mind, ChalksError("Avatar without mind trying to collaborate in")
        self.node.add_site(self.mind) # we register our perspective in the parent
        print "Registering child perspective %s" % self.mind
        
        # we obtain and return the required data to start the session in the child
        t_state = self.node.get_state(); t_state = list(t_state);
        # Convert HB Operation objects to diccionaries
        t_HB = t_state[3]; t_HB = map(dict, t_HB); t_state[3] = t_HB;
        
        # return the parent ChalksNode reference, and the data necesarry to start the collaboration
        return t_state
        
    
    def perspective_collaborate_out(self):
        """
        Logout from the collaborative server associated to the selected node
        """
    
        # logout of the Collaborative Node
        self.node.del_client(self)
        
        self.site_id = None
        
        return
        
    #@nonl
    #@-node:rodrigob.20040126020641:collaborate in/out
    #@+node:rodrigob.20040129150513:logout
    def logout(self,):
        """
        This methods is called when the children node is disconnecting himself
        """
        
        # <<<< EDIT CODE # has to generate the propagation of a disconnection notification to all the other nodes....
        
        print "Avatar is login out self.avatarId == %s" % self.avatarId # just for debugging
        print "User '%s' is quiting the session" % self.nickname
            
        return
    #@-node:rodrigob.20040129150513:logout
    #@+node:rodrigob.20040915120517:bi directional methods
    #@+at
    # this methods are common to both children->parent calls and 
    # parent->childrens calls.
    # So we use only one implementation. ChalksAvatar calls ChalksNode 
    # implementation.
    #@-at
    #@@c
    #@nonl
    #@+node:rodrigob.20040915120517.1:send message
    def perspective_send_message(self, from_, to, txt):
        """ 
        Send a message to
        """
        return self.node.remote_send_message(self.mind, from_, to, txt)
        
    #@nonl
    #@-node:rodrigob.20040915120517.1:send message
    #@+node:rodrigob.20040915120517.2:receive operation
    def perspective_receive_operation(self, in_op, *args, **kw):
        """
        """
        return self.node.remote_receive_operation(self.mind, in_op, *args, **kw)
        
    perspective_receive_op = perspective_receive_operation
    #@-node:rodrigob.20040915120517.2:receive operation
    #@-node:rodrigob.20040915120517:bi directional methods
    #@-others
#@nonl
#@-node:rodrigob.20040125194534:class ChalksAvatar
#@+node:niederberger.20040909124137:class ChalksServerMonitor
class ChalksServerMonitor(object):
    """ 
    This class provides removeService and addService methods for Rendezvous module's ServiceBrowser().
    The one responsible for creating this object should call self.stop() when not using it any more.
    Ins tead of calling getServers() every once in a while, you can register your callback funcion with addCallbackListener()
    Users of this class should only call the getServers() method, which should return a dict of known local servers, keyed by server name. Each entry is a server, 
    represented as a dictionary with the following keys:
        "address": ip address
        "identifier": user supplied string identifier for this service
        "port": integer port

    """
    def __init__(self):
        self.servers =  {} # known servers
        self.rendezvous = None # the one and only Rendezvous instance
        self.browser = None # the one and only Service browser
        self.cb_listeners = [] # list of callback functions
        self.startListening()  # make it active        

    def removeService(self, rendezvous, type, name):
        """ this is a callback method and should not be called externally
        """
        print "Server", name, "removed"
        try:
            del self.servers[name]
        except KeyError:
            print "attempt to remove unknown server"
            
        # invoke callback functions
        for t_cb in self.cb_listeners:
            t_cb(self.getServers())            

    def addService(self, rendezvous, type, name):
        """ this is a callback method and should not be called externally
        """        
        info = rendezvous.getServiceInfo(type, name)
        
        #print 'New server', name, info
        
        self.servers[name] = {'address':     info.getAddress(),
                              'identifier':  info.getName(),
                              'port':        info.getPort(),
                              }                              

        # invoke callback functions
        for t_cb in self.cb_listeners:
            t_cb(self.getServers())

    def addCallbackListener(self, cbFcn):
        """
        call this to register your callback function called whenever a server is detected/removed. This function should accept the server list as a parameter
        """
        self.cb_listeners.append(cbFcn)
        
    def removeCallbackListener(self, cbFcn):
        """
        call this to unregister your callback function
        """
        try:
            self.cb_listeners.remove(cbFcn)
        except ValueError:
            print 'attempt to remove callback not found on callback list'

    def getServers(self):
        return self.servers
        
    def startListening(self):
        assert (self.rendezvous is None) and (self.browser is None), 'you can only call this method once'
        from Rendezvous import Rendezvous, ServiceBrowser
        try:
            self.rendezvous = Rendezvous() # <<<< crashes if no internet available
        except:
            print "Error starting rendezvous browser. Automatic discovery of local servers is disabled."
        else:
            t_type = "_chalks._tcp.local."
            self.browser = ServiceBrowser(self.rendezvous, t_type, self)
            print "Started listening local network for Chalks servers ..."
                
    def stop(self):
        assert self.browser, 'you should only call stop() when there is a browser/rendevzvous threads running'
        self.browser.cancel()
        self.rendezvous.close()
        print "Stopping RendezVous service browser..."
            
    def registerService(self, name, host, port, owner = "unknown", private = 0):
        """ 
        Registers a service provider with the supplied parameters on mDNS records.  Parameter examples:

        host = "10.64.97.7"
        port = 9870
        name = "My test CHalks server"
        owner = "John Smith"
        private = 0    # 0 or 1, if it requires a key to join
        
        """
        from Rendezvous import Rendezvous, ServiceInfo
        from Rendezvous import NonUniqueNameException
        import socket
        
        print "Registering your server with rendezvous ..."        
        # register record with Rendezvous
        r = Rendezvous()
        desc = {'owner':owner,
                'private': str(private),
                }
        info = ServiceInfo("_chalks._tcp.local.", name + "._chalks._tcp.local.", socket.inet_aton(host), port, 0, 0, desc)
        try:
            r.registerService(info)
        except NonUniqueNameException:
            print "Unable to advertise your shared file on the local network: Apparently there is a service with this same name."

#@-node:niederberger.20040909124137:class ChalksServerMonitor
#@+node:rodrigob.20040127180819:class ChalksError
class ChalksError(pb.Error):
    """
    Own error kind
    """
    
    pass
    
#@nonl
#@-node:rodrigob.20040127180819:class ChalksError
#@+node:rodrigob.20040130123655:main
if __name__ == '__main__':
    #test_FileStack()
    app = Chalks()
    reactor.run()
#@-node:rodrigob.20040130123655:main
#@-others



#@-node:rodrigob.20040119132914:@thin Chalks.py
#@-leo
