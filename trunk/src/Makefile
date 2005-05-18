all: chalks.exe

linux = 1

#ifeq ($(MAKE), make) ? or nmake ?

ifeq ($(linux), 1) #linux
  rmCommand = rm -f
  GtkDllResources = -pkg:glade-sharp-2.0
else #windows
  rmCommand = del /F
  GtkDllResources = -r:glade-sharp.dll -r:glib-sharp.dll -r:pango-sharp.dll -r:atk-sharp.dll -r:gdk-sharp.dll -r:gtk-sharp.dll
endif

# -pkg:gtksourceview-sharp

Compiler = ncc.exe

DllResources = $(GtkDllResources) -r:Nini.dll -r:System.Runtime.Remoting.dll 
Resources =  -res:chalks.glade -res:chalks.ico
Flags = -g

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

chalks.exe: chalks.glade chalks.ico Chalks.n Gui.n ConcurrentEditionWidget.n chalks_core.dll
	$(rmCommand) chalks.exe
	$(Compiler) $(Flags) -t:exe -out:"chalks.exe" $(Resources) -r:chalks_core.dll $(DllResources)  Chalks.n Gui.n ConcurrentEditionWidget.n

chalks_core.dll: ConcurrentEdition.n Network.n Helpers.n
	$(rmCommand) *.exe
	$(Compiler) $(Flags) -t:library -out:"chalks_core.dll" $(DllResources) ConcurrentEdition.n Network.n Helpers.n

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

nunits: test_network.dll test_cce.dll
	nunit-console test_cce.dll test_network.dll /labels

test_network.dll: TestNetwork.n chalks_core.dll Gui.n ConcurrentEditionWidget.n 
	$(Compiler) $(Flags) -t:library -out:"test_network.dll" -r:nunit.framework.dll $(DllResources) -r:chalks_core.dll TestNetwork.n  Gui.n ConcurrentEditionWidget.n

test_cce.dll: TestConcurrentEdition.n chalks_core.dll Gui.n ConcurrentEditionWidget.n 
	$(Compiler) $(Flags) -t:library -out:"test_cce.dll" -r:nunit.framework.dll  $(DllResources) -r:chalks_core.dll TestConcurrentEdition.n Gui.n ConcurrentEditionWidget.n

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

test: test_network.exe test_cce.exe


test_network.exe: TestNetwork.n  Gui.n ConcurrentEditionWidget.n chalks_core.dll
	$(rmCommand) test_network.exe
	$(Compiler) $(Flags) -out:"test_network.exe" -r:nunit.framework.dll $(DllResources) -r:chalks_core.dll TestNetwork.n  Gui.n ConcurrentEditionWidget.n
	./test_network.exe	

test_cce.exe: TestConcurrentEdition.n Gui.n ConcurrentEditionWidget.n chalks_core.dll
	$(rmCommand) test_cce.exe
	$(Compiler) $(Flags) -out:"test_cce.exe" -r:nunit.framework.dll  $(DllResources) -r:chalks_core.dll TestConcurrentEdition.n  Gui.n ConcurrentEditionWidget.n
	./test_cce.exe	

# -~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

clean:
	$(rmCommand) *.exe *~ test_*.dll chalks_core.dll TestResult.xml chalks.config \#*\#
