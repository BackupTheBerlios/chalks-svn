#! /usr/bin/env python

import os
import os.path
import sys

# main() is at the end of the file

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# Global variables

if os.name in ["posix", "cygwin"]:
    GtkDllResources = "-pkg:glade-sharp-2.0 "
    RemoveCommand = "rm -f "
elif os.name in ["win32", "nt"]:
    GtkDllResources =  "-r:glade-sharp.dll -r:glib-sharp.dll" \
                     + "-r:pango-sharp.dll -r:atk-sharp.dll" \
                     + "-r:gdk-sharp.dll -r:gtk-sharp.dll "
    RemoveCommand = "del /F "
else: 
    raise "Unknown os named %s" % os.name


Compiler = "ncc.exe "

DllResources = GtkDllResources + "-r:Nini.dll -r:System.Runtime.Remoting.dll " 
Resources =  "-res:chalks.glade -res:chalks.ico "
Flags = "-g "


# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

def build(target):
    if   target == "chalks.exe":
        chalks()
    elif target == "chalks_core.dll":
        chalks_core()
    elif target == "clean":
        clean()
    elif target == "test":
        test()
    elif target == "nunits":
        nunits()
    else:
        raise "No method to build the target %s" % target

    return


def chalks():
    
    target = "chalks.exe"
    
    resources = ["chalks.glade", "chalks.ico"]
    compiled_sources = ["chalks_core.dll"]
    compilable_sources = ["Chalks.n", "Gui.n", "ConcurrentEditionWidget.n"]
    sources =  resources + compiled_sources + compilable_sources

    for source in compiled_sources:
        if not os.path.exists(source):
            build(source)

    ret = is_older(target, sources)
    
    if ret:
        print "Building %s" % target
        if os.path.exists(target):
            os.remove(target)

        build_command = Compiler + Flags \
                        + '-t:exe -out:"chalks.exe" ' \
                        + Resources + "-r:chalks_core.dll " + DllResources \
                        + " ".join(compilable_sources)
        print "Executing:\n%s\n" % build_command
        ret = os.system(build_command)
        if ret != 0:
            raise "Error during the compilation"
    else:
        print "%s is up to date" % target
        
    return



def chalks_core():
    
    target = "chalks_core.dll"

    resources = []
    compiled_sources = []
    compilable_sources = ["ConcurrentEdition.n", "Network.n", "Helpers.n"]
    sources =  resources + compiled_sources + compilable_sources
    
    for source in compiled_sources:
        if not os.path.exists(source):
            build(source)

    ret = is_older(target, sources)
    
    if ret:
        print "Building %s" % target
        os.system(RemoveCommand + "*.exe")
                
        if os.path.exists(target):
            os.remove(target)
        
        build_command = Compiler + Flags \
                        + '-t:library -out:"chalks_core.dll" ' \
                        + DllResources \
                        + " ".join(compilable_sources)
        print "Executing:\n%s\n" % build_command
        ret = os.system(build_command)
        if ret != 0:
            raise "Error during the compilation"
        
    else:
        print "%s is up to date" % target

    return


def clean():

    command = RemoveCommand \
              + " *.exe *~ test_*.dll chalks_core.dll TestResult.xml chalks.config \#*\#"

    print "Executing:\n%s\n" % command
    os.system(command)

    return

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

def test():
    '''
    test: test_network.exe test_cce.exe


test_network.exe: TestNetwork.n  Gui.n ConcurrentEditionWidget.n chalks_core.dll
	$(rmCommand) test_network.exe
	$(Compiler) $(Flags) -out:"test_network.exe" -r:nunit.framework.dll $(DllResources) -r:chalks_core.dll TestNetwork.n  Gui.n ConcurrentEditionWidget.n
	./test_network.exe	

test_cce.exe: TestConcurrentEdition.n Gui.n ConcurrentEditionWidget.n chalks_core.dll
	$(rmCommand) test_cce.exe
	$(Compiler) $(Flags) -out:"test_cce.exe" -r:nunit.framework.dll  $(DllResources) -r:chalks_core.dll TestConcurrentEdition.n  Gui.n ConcurrentEditionWidget.n
	./test_cce.exe	

    '''
    raise "to be implemented"
    return

def nunits():
    '''
    nunits: test_network.dll test_cce.dll
	nunit-console test_cce.dll test_network.dll /labels

test_network.dll: TestNetwork.n chalks_core.dll Gui.n ConcurrentEditionWidget.n 
	$(Compiler) $(Flags) -t:library -out:"test_network.dll" -r:nunit.framework.dll $(DllResources) -r:chalks_core.dll TestNetwork.n  Gui.n ConcurrentEditionWidget.n

test_cce.dll: TestConcurrentEdition.n chalks_core.dll Gui.n ConcurrentEditionWidget.n 
	$(Compiler) $(Flags) -t:library -out:"test_cce.dll" -r:nunit.framework.dll  $(DllResources) -r:chalks_core.dll TestConcurrentEdition.n Gui.n ConcurrentEditionWidget.n
    
    '''
    
    raise "to be implemented"
    return

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

# Helper methods

def is_older(target, sources):
    # check modification time
    # return the list of newer files
    
    if not os.path.exists(target):
        return sources
    
    ret = []
    target_mtime = os.stat(target).st_mtime;
    for source in sources:
        if os.stat(target).st_mtime > target_mtime:
            ret.add(source)

    return ret

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
def main():    
    arg = sys.argv[-1] 

    if arg and len(sys.argv) > 1:
        build(arg)
    else:
        build("chalks.exe")
    
if __name__ == "__main__":
    main()
