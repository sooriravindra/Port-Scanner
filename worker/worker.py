# autobahn imports
from os import environ
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks

class Component(ApplicationSession):

    def startScan(self):
        print("Starting port scan")
        # port scanner
        
    def onJoin(self, details):
        print("session attached")
        self.subscribe(self.startScan, "scan.start")
        
    def onDisconnect(self):
        print("disconnected")
        if reactor.running:
            reactor.stop()

if __name__ == '__main__':
    import six
    url = environ.get("CBURL", u"ws://127.0.0.1:80/ws")
    if six.PY2 and type(url) == six.binary_type:
        url = url.decode('utf8')
    realm = environ.get('CBREALM', u'realm1')
    runner = ApplicationRunner(url, realm)
    runner.run(Component)
