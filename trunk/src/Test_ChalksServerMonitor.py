import unittest
from Chalks import ChalksServerMonitor

class Monitor(unittest.TestCase):
  def testLaunchAndClose(self):
    sm = ChalksServerMonitor()
    sm.stop()

  def testGetEmptyServers(self):
    sm = ChalksServerMonitor()
    servers = sm.getServers()
    assert not len(servers)
    sm.stop()

  def testGetServers(self):
    sm = ChalksServerMonitor()
    sm.registerService('test server', '127.0.0.1', 8888, "test dude")
    sm.registerService('test server 2', '127.0.0.1', 8888, "test dude")
    servers = sm.getServers()
    assert len(servers) == 2
    sm.stop()

if __name__ == '__main__':
  unittest.main()