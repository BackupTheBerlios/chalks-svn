#!/usr/bin/env python

try:
    from distutils.core import setup
except:
    import traceback
    import sys
    
    traceback.print_exc()
    print "Unable to import python distutils."
    print "You may want to install the python-dev package on your distribution."
    sys.exit(1)

import os
if os.name in ["nt","dos",'win32']:                   # Windows systems
    import py2exe

setup(name='Chalks',
      version='0.1',      
      #packages=['src'],
      scripts=['Chalks.py'],   # for *NIX
      windows = [              # for Windows
         {  "script": "Chalks.py", 
            "icon_resources": [(1, "chalks.ico")] 
         }
                ],       
      data_files = [("",["Chalks.xhtml", "chalks.ico"],),],
      description="crossplatform realtime concurrent editing",
      long_description ="""Chalks is a software under development for crossplatform realtime concurrent editing. The primary focus will be ease of use and minimum requirements.""",
      author="Chalks development team",
      url="http://chalks.berlios.de/",
      platforms = ['Linux','Windows'],
      license = 'GPL2',      
      )


