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

# change it to whatever you want to; we are more comfortable with MySQL as a backend
# Redis could have been used as a backend too 
result_backend = 'db+mysql://root:123@127.0.0.1:3306/test'
# use redis or rabbitmq; rabbitmq is more reliable though
app = Celery('tasks', backend=result_backend, broker='redis://localhost')

# URG = 0x20
# ACK = 0x10
# PSH = 0x08
# RST = 0x04
# SYN = 0x02
# FIN = 0x01

@task_prerun.connect()
def prerun(sender=None, **kwds):
	
	task_id = kwds['task_id']
	args = kwds['kwargs']['it']
	master_task_id = args[0][0]

	associate_master_celery_task(master_task_id, task_id)

def is_icmp_blocked(response):
	if response.haslayer(ICMP):
		icmp_layer = response.getlayer(ICMP)
		blocked = int(icmp_layer.type) == 3 and (int(icmp_layer.code) in [1,2,3,9,10,13])
		if blocked:
			return 1
		
		return 0

	# unknown
	return -1

@app.task(name="ping-scan")
def ping_scan(master_task_id, dest_ip):
	timeout = 5
	response = sr1(IP(dst=str(dest_ip))/ICMP(), timeout=timeout)
 
	if response is None or is_icmp_blocked(response):
		return {"status" : "unknown"} 
	else:
		return {"status" : "alive", "ip" : dest_ip, "scan_type" : "ping_sweep"} 

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
			return {"status" : "open", "payload" : "", "ip" : dest_ip, "port" : dport, "scan_type" : "syn_scan"}
		# port is closed ACK|RST
		elif response.getlayer(TCP).flags == 0x14:
			return {"status" : "closed", "payload" : ""}

@app.task(name="fyn-scan")
def fyn_scan(master_task_id, dest_ip, dport):

	sport = RandShort()
	timeout = 10
	
	response = sr1(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="F"), timeout=timeout)

	# if you do not get a response then the port is open
	if response is None:
		return {"status" : "open", "payload" : "", "ip" : dest_ip, "port" : dport, "scan_type" : "fyn_scan"}

	# if you get a RST then the port is definiely closed
	elif response.haslayer(TCP):
		if response.getlayer(TCP).flags == 0x14:
			return {"status" : "closed", "payload" : ""}
	
	# packets have been filtered/dropped by the firewall
	# so you would not know the status of the port
	elif is_icmp_blocked(response) > 0:
		return {"status" : "unknown", "payload" : "Blocked by Firewall"}
	
@app.task(name="grab-banner")
def grab_banner(master_task_id, dest_ip, dport):
	print(dest_ip, dport)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
			banner = s.recv(4096)
			banner = banner.decode("utf-8")


	except socket.error as e:
			return {"status" : "closed", "payload" : ""}

	s.close()

	return {"status" : "open", "payload" : banner, "ip" : dest_ip, "port" : dport, "scan_type" : "banner_grab"}