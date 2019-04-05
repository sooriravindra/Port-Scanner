def distributeJobs(ip,startPort,endPort):
	workersCount = len(workers)
	portsPerWorker = (endPort - startPort)/workersCount
	for worker,port in enumerate(range(startPort,endPort,portsPerWorker)):
		print(worker%workersCount, ip, port, port + min(portsPerWorker, endPort - port))

ip="1.1.1.1"
startPort=20
endPort = 91
workers = [1,2]
distributeJobs(ip,startPort,endPort)
