# autobahn imports
from os import environ
from twisted.internet import reactor
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from scanner import start_scan


class Component(ApplicationSession):

    # very simplistic way to start
    def generateWorkerId(self):
        return len(workers) + 1

    def registerWorker(self):
        print("Registering Worker")
        workerId  = self.generateWorkerId()
        workers.append(workerId)
        self.publish("scan.worker.registration_success",workerId)

    # receive the scanned results
    def scanResults(self,workerId,status):
        print("Retrieving scanned results")

    # distribute the jobs amongst the workers
    # sample distribution logic; considering only ports distributions for the time being 
    def distributeJobs(self, ip,startPort,endPort):
        workersCount = len(workers)
        portsPerWorker = (endPort - startPort)/workersCount
        for worker,port in enumerate(range(startPort,endPort,portsPerWorker)):
            self.publish("scan.worker{}.allot".format(worker%workersCount), ip, port, min(portsPerWorker, endPort - port))
    
    def startScan(self, params):
        # port scanner
        dest_ip = params['ip_address'] 
        network_prefix = params['network_prefix'] 
        start_port = int(params['start_port']) 
        end_port = int(params['end_port']) 
        scan_mode = params['scan_mode'] 

        timeout = 2
        # this will be disributed among the workers
        for port in range(start_port,end_port + 1):
            status = start_scan(scan_mode,dest_ip,port,timeout)
            self.publish("scan.result",{"ip" :  dest_ip, "port" : port, "status" : status})
        
    def onJoin(self, details):
        print("session attached")
        self.workers = []
        self.subscribe(self.startScan, "scan.start")
        self.subscribe(self.scanResults, "scan.worker.result")
        self.subscribe(self.registerWorker, "scan.worker.register")
        
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