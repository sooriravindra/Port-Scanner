# autobahn imports
from os import environ
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks
from scanner import start_scan


class Component(ApplicationSession):

    @inlineCallbacks
    def startScan(self, params):
        # port scanner
        dest_ip = params['ip_address'] 
        network_prefix = params['network_prefix'] 
        start_port = int(params['start_port']) 
        end_port = int(params['end_port']) 
        scan_mode = params['scan_mode'] 

        timeout = 3

        for port in range(start_port,end_port):
            print(port)
            status = start_scan(scan_mode,dest_ip,start_port,timeout)
            print(port,status)
            yield self.publish("scan.result",{"ip" :  dest_ip, "port" : port, "status" : status})
        
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
