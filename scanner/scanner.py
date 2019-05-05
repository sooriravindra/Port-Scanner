#! /usr/bin/env python3

from scapy.all import *
import socket
# for parsing http raw headers
# https://stackoverflow.com/questions/4685217/parse-raw-http-headers
import email
import io
import json 
from celery import Celery
from celery.signals import task_prerun
from db import associate_master_celery_task
from utils import get_current_time

# change it to whatever you want to; we are more comfortable with MySQL as a backend
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'db+mysql://root:123@127.0.0.1:3306/test')

app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

 
# URG = 0x20
# ACK = 0x10
# PSH = 0x08
# RST = 0x04
# SYN = 0x02
# FIN = 0x01

@task_prerun.connect()
def prerun(sender=None, **kwds):
	
	task_id = kwds['task_id']
	if len(kwds['args']) == 0:
		args = kwds['kwargs']['it']
		master_task_id = args[0][0]
	else:
		args = kwds['args']
		master_task_id = args[0]

	associate_master_celery_task(master_task_id, task_id)

def is_icmp_blocked(response):
	if response.haslayer(ICMP):
		icmp_layer = response.getlayer(ICMP)
		blocked = int(icmp_layer.type) == 3 and (int(icmp_layer.code) in [1,2,3,9,10,13])
		if blocked:
			return True
		
		return False

	return True

def checkCommonServices(dest_ip):

	# just a sample list; you could add custom ports to these
	portList = [80, 21, 22, 23, 25, 53, 443, 3306, 8080]

	for port in portList:
		try:  
			s = socket.socket()
			s.settimeout(2)
			s.connect((dest_ip, port))  
			return True
		except:  
			pass 

	return False

@app.task(name="ping-scan")
def ping_scan(master_task_id, dest_ip):
	timeout = 5
	response = sr1(IP(dst=str(dest_ip))/ICMP(), timeout=timeout)

	if response is None or is_icmp_blocked(response):
		# check if any services on common ports are running; if icmp is blocked
		if checkCommonServices(dest_ip):
			return {"status" : "alive", "ip" : dest_ip, "payload" : json.dumps({"finish_time" : get_current_time()})} 
		
		return {"status" : "not-alive"} 
	else:
		return {"status" : "alive", "ip" : dest_ip, "payload" : json.dumps({"finish_time" : get_current_time()}) } 

@app.task(name="syn-scan")
def syn_scan(master_task_id, dest_ip, dport):
	
	sport = RandShort()
	timeout = 10
	
	response = sr1( IP(dst=dest_ip) / TCP(sport=sport,dport=dport,flags="S"),timeout=timeout)
	
	if response is None:
		return {"status" : "unknown", "payload" : "No Response"}

	if response.haslayer(TCP):
		# if 20 then its closed; then the server responded with SYN|ACK
		if response.getlayer(TCP).flags == 0x12:
			# send rst if the kernel fails to send
			send_rst = send(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="R"))
			return {"status" : "open", "payload" : json.dumps({"finish_time" : get_current_time()}), "ip" : dest_ip, "port" : dport}
		# port is closed ACK|RST
		elif response.getlayer(TCP).flags == 0x14:
			return {"status" : "closed", "payload" : ""}

	# packets have been filtered/dropped by the firewall
	# so you would not know the status of the port
	elif is_icmp_blocked(response):
		return {"status" : "unknown", "payload" : "Filtered"}

@app.task(name="fyn-scan")
def fyn_scan(master_task_id, dest_ip, dport):

	sport = RandShort()
	timeout = 10
	
	response = sr1(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="F"), timeout=timeout)

	# if you do not get a response then the port is open
	if response is None:
		return {"status" : "open", "payload" : json.dumps({"finish_time" : get_current_time()}), "ip" : dest_ip, "port" : dport}

	# if you get a RST then the port is definiely closed
	elif response.haslayer(TCP):
		if response.getlayer(TCP).flags == 0x14:
			return {"status" : "closed", "payload" : ""}
	
	# packets have been filtered/dropped by the firewall
	# so you would not know the status of the port
	elif is_icmp_blocked(response):
		return {"status" : "unknown", "payload" : "Filtered"}
	
@app.task(name="grab-banner")
def grab_banner(master_task_id, dest_ip, dport):
	
	s = socket.socket()
	s.settimeout(10)
	banner = ""
	try:
		s.connect((dest_ip, dport))
		if dport == 80:
			#Now make a HTTP GET request to the server over the established TCP connection
			message = "GET / HTTP/1.1\r\n\r\n"
			s.sendall(message.encode())
			banner = s.recv(4096)
			# parse the http response
			banner = banner.decode('utf-8')
			request_line, headers_alone = banner.split('\r\n', 1)
			message = email.message_from_file(io.StringIO(headers_alone))
			banner = dict(message.items())
			banner = json.dumps(banner)
		else:
			message = "I am sending you garbage? \r\n" 
			s.send(message.encode())
			banner = s.recv(4096)
			banner = banner.decode("utf-8")


	except socket.error as e:
			return {"status" : "closed", "payload" : ""}

	s.close()

	return {"status" : "open", "payload" : banner, "ip" : dest_ip, "port" : dport}