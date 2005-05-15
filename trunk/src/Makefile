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

DllResources = $(GtkDllResources) -r:Nini.dll -r:System.Runtime.Remoting.dll -r:helpers.dll
Resources =  -res:chalks.glade -res:chalks.ico
Flags = 

chalks.exe: chalks.glade chalks.ico Chalks.n Gui.n ConcurrentEditionWidget.n ConcurrentEdition.n Network.n helpers.dll
	$(rmCommand) chalks.exe
	$(Compiler) $(Flags) -out:"chalks.exe" $(Resources) $(DllResources) Chalks.n Gui.n ConcurrentEditionWidget.n Network.n ConcurrentEdition.n

helpers.dll: Helpers.n
	$(rmCommand) *.exe
	$(Compiler) $(Flags) -t:dll -out:"helpers.dll" Helpers.n
#-r:Nemerle.Compiler.dll # required if using macros

nunits: test_network.dll test_cce.dll
	nunit-console test_cce.dll test_network.dll /labels

test_network.dll: TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(Compiler) $(Flags) -t:library -out:"test_network.dll" -r:nunit.framework.dll $(DllResources) TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n

test_cce.dll: TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(Compiler) $(Flags) -t:library -out:"test_cce.dll" -r:nunit.framework.dll  $(DllResources) TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n


test: test_network.exe test_cce.exe
	./test_network.exe
	./test_cce.exe	

test_network.exe: TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(rmCommand) test_network.exe
	$(Compiler) $(Flags) -out:"test_network.exe" -r:nunit.framework.dll $(DllResources) TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n

test_cce.exe: TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(rmCommand) test_cce.exe
	$(Compiler) $(Flags) -out:"test_cce.exe" -r:nunit.framework.dll  $(DllResources) TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n

clean:
	$(rmCommand) *.exe *~ test_*.dll helpers.dll TestResult.xml chalks.config
