all: chalks.exe

DllResources = -r:System.Runtime.Remoting.dll -pkg:glade-sharp-2.0 -pkg:gtk-sharp-2.0 -pkg:gtksourceview-sharp -r:Nini.dll
Resources =  -res:chalks.glade -res:chalks.ico
Flags =

chalks.exe: chalks.glade chalks.ico Chalks.n Gui.n ConcurrentEditionWidget.n ConcurrentEdition.n Network.n
	rm -f chalks.exe
	ncc.exe $(Flags) -out:"chalks.exe" $(DllResources) $(Resources) Chalks.n Gui.n ConcurrentEditionWidget.n ConcurrentEdition.n Network.n


test: test_network.dll test_cce.dll
	nunit-console test_cce.dll test_network.dll

test_network.dll: TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n
	ncc $(Flags) -t:library -out:"test_network.dll" -r:nunit.framework.dll $(DllResources) TestNetwork.n Network.n ConcurrentEdition.n Gui.n ConcurrentEditionWidget.n

test_cce.dll: TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n
	ncc $(Flags) -t:library -out:"test_cce.dll" -r:nunit.framework.dll  $(DllResources) TestConcurrentEdition.n ConcurrentEdition.n Network.n Gui.n ConcurrentEditionWidget.n


clean:
	rm -f *.exe *~ test_*.dll TestResult.xml chalks.config
