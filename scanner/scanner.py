#! /usr/bin/env python3

from scapy.all import *
import socket
import errno
# for parsing http raw headers
# https://stackoverflow.com/questions/4685217/parse-raw-http-headers
import email
import io
import json 
from celery import Celery
from celery.signals import task_postrun
from datetime import datetime

# https://stackoverflow.com/questions/39574813/error-loading-mysqldb-module-no-module-named-mysqldb/39575525
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

# change it to whatever you want to; 
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
# this has to be used in conjunction with result backend 
@task_postrun.connect()
def task_postrun(sender=None, **kwds):
	
	db = MySQLdb.connect(host="127.0.0.1",
                 user="root",
                 passwd="123",
                 db="test")
	
	task_id = kwds['task_id']
	task_name = kwds['task'].name
	state = kwds['state']
	task_result = kwds['retval']
	args = kwds['args']
	ip = args[0]
	port = args[1]

	cursor = db.cursor()
	cursor.execute(
		'INSERT INTO celery_tasks (task_id, task_name, task_result, state, ip, port) VALUES (%s,%s,%s,%s,%s,%s)',
		(task_id, task_name, task_result, state, ip, port)
	)

	db.commit()
	db.close()

@app.task(name="syn-scan")
def syn_scan(dest_ip, dport):
	
	sport = RandShort()
	timeout = 2
	
	response = sr1( IP(dst=dest_ip) /TCP(sport=sport,dport=dport,flags="S"),timeout=timeout)
	
	if response is None:
		return -1

	if response.haslayer(TCP):
		# if 20 then its closed; then the server responded with SYN|ACK
		if response.getlayer(TCP).flags == 0x12:
			# send rst if the kernel fails to send
			send_rst = send(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="R"))
			return 1
		# port is closed ACK|RST
		elif response.getlayer(TCP).flags == 0x14:
			return 0

@app.task(name="fyn-scan")
def fyn_scan(dest_ip, dport):

	sport = RandShort()
	timeout = 10
	
	response = sr1(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="F"))

	if response is None:
		return 1

	elif response.haslayer(TCP):
		if response.getlayer(TCP).flags == 0x14:
			return 0
	
	elif(response.haslayer(ICMP)):
		# packets have been filtered/dropped by the firewall
		if (int(response.getlayer(ICMP).type)==3 and int(response.getlayer(ICMP).code) in [1,2,3,9,10,13]):
			return 2
	
@app.task(name="grab-banner")
def grab_banner(dest_ip, dport):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10)
	banner = ""
	try:
		s.connect((dest_ip, dport))
		if dport == 80:
			#Send some data to remote server
			message = "GET / HTTP/1.1\r\n\r\n"
			s.sendall(message.encode())
			banner = s.recv(4096)
			banner = banner.decode('utf-8')
			request_line, headers_alone = banner.split('\r\n', 1)
			message = email.message_from_file(io.StringIO(headers_alone))
			banner = dict(message.items())
			banner = json.dumps(banner)
		else:
			banner = s.recv(4096)
			banner = banner.decode("utf-8")


	except socket.error as e:
		if e.errno == errno.ECONNREFUSED:
			print("Connection refused")
		else:
			print(e)
	s.close()

	return banner 



# host = "espncricinfo.com"
# dport = 22
# dest_ip = socket.gethostbyname(host)
# # dest_ip  = "45.33.32.156"
# # print(dest_ip)
# response = fyn_scan(dest_ip, dport)
# print(response)

