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
from datetime import datetime

# https://stackoverflow.com/questions/39574813/error-loading-mysqldb-module-no-module-named-mysqldb/39575525
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

# change it to whatever you want to; we are more comfortable with MySQL as a backend
# Redis could have been used as a backend too 
result_backend = 'db+mysql://root:123@127.0.0.1:3306/test'
# use redis or rabbitmq; rabbitmq is more reliable though
app = Celery('tasks', backend=result_backend, broker='redis://localhost')

# -1 is unanswered
# 1 is open
# 0 is closed
# URG = 0x20
# ACK = 0x10
# PSH = 0x08
# RST = 0x04
# SYN = 0x02
# FIN = 0x01

#SYN|ACK = 0x12
#ACK|RST = 0x14

# opening and closing db connections very expensive; couldn't figure out a init and shutdown hook
# worker_init, worker_shutdown these are the hooks
# the reason for this is that arguments of the pending tasks is never known
# this has to be used in conjunction with result backend 
# insert it into database; pass master task as the argument
@task_prerun.connect()
def prerun(sender=None, **kwds):
	
	db = MySQLdb.connect(host="127.0.0.1",
				 user="root",
				 passwd="123",
				 db="test")
	

	task_id = kwds['task_id']
	args = kwds['kwargs']['it']
	master_task_id = args[0][2]

	cursor = db.cursor()
	cursor.execute(
		'INSERT INTO `celery_tasks` (`master_task_id`, `task_id`) \
		VALUES (%s,%s)',
		(master_task_id, task_id)
	)

	db.commit()
	db.close()


def is_icmp_blocked(response):
	if response.haslayer(ICMP):
		icmp_layer = response.getlayer(ICMP)
		blocked = int(icmp_layer.type) == 3 and (int(icmp_layer.code) in [1,2,3,9,10,13])
		if blocked:
			return 1
		
		return 0

	return 1

def is_host_alive(host):
	timeout = 5
	response = sr1(IP(dst=str(host))/ICMP(), timeout=timeout)
 
	if response is None or is_icmp_blocked(response):
		return 0
	else:
		return 1 

@app.task(name="syn-scan")
def syn_scan(dest_ip, dport, master_task_id):
	
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
def fyn_scan(dest_ip, dport, master_task_id):

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
	elif(response.haslayer(ICMP)):
		if (int(response.getlayer(ICMP).type)==3 and int(response.getlayer(ICMP).code) in [1,2,3,9,10,13]):
			return {"status" : "unknown", "payload" : "Blocked by Firewall"}
	
@app.task(name="grab-banner")
def grab_banner(dest_ip, dport, master_task_id):
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



# host = "espncricinfo.com"
# dport = 22
# dest_ip = socket.gethostbyname(host)
# # dest_ip  = "45.33.32.156"
# # print(dest_ip)
# response = fyn_scan(dest_ip, dport)
# print(response)

