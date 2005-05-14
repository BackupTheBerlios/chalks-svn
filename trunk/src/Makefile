all: chalks.exe

# make.exe aviable at http://unxutils.sourceforge.net/

#rmCommand = del /F
rmCommand = rm -f

Compiler = ncc.exe
DllResources = -pkg:gtk-sharp-2.0,glade-sharp-2.0 -r:Nini.dll -r:System.Runtime.Remoting.dll -r:helpers.dll #-pkg:gtksourceview-sharp

Resources =  -res:chalks.glade -res:chalks.ico
Flags =

chalks.exe: chalks.glade chalks.ico Chalks.n Gui.n ConcurrentEditionWidget.n ConcurrentEdition.n Network.n helpers.dll
	$(rmCommand) chalks.exe
	$(Compiler) $(Flags) -out:"chalks.exe" $(DllResources) $(Resources) Chalks.n Gui.n ConcurrentEditionWidget.n ConcurrentEdition.n Network.n

helpers.dll: Helpers.n
	$(rmCommand) *.exe
	$(Compiler) $(Flags)-r:Nemerle.Compiler.dll -t:dll -out:"helpers.dll" Helpers.n

test: test_network.dll test_cce.dll
	nunit-console test_cce.dll test_network.dll /labels

test_network.dll: TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(Compiler) $(Flags) -t:library -out:"test_network.dll" -r:nunit.framework.dll $(DllResources) TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n

test_cce.dll: TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(Compiler) $(Flags) -t:library -out:"test_cce.dll" -r:nunit.framework.dll  $(DllResources) TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n

test_network.exe: TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(rmCommand) test_network.exe
	$(Compiler) $(Flags) -out:"test_network.exe" -r:nunit.framework.dll $(DllResources) TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n

test_cce.exe: TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n helpers.dll
	$(rmCommand) test_cce.exe
	$(Compiler) $(Flags) -out:"test_cce.exe" -r:nunit.framework.dll  $(DllResources) TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n

clean:
	$(rmCommand) *.exe *~ test_*.dll helpers.dll TestResult.xml chalks.config
