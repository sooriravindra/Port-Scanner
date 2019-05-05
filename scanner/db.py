#!/usr/bin/python
import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb
import pickle
import os

mysql_host = os.environ.get('MYSQL_HOST', '127.0.0.1')

def associate_master_celery_task(master_task_id, task_id):
	db = MySQLdb.connect(host=mysql_host,
				 user="root",
				 passwd="123",
				 db="test")
	
	cursor = db.cursor()
	cursor.execute(
		'INSERT INTO `celery_tasks` (`master_task_id`, `task_id`) \
		VALUES (%s,%s)',
		(master_task_id, task_id)
	)

	db.commit()
	db.close()


def create_master_task(ip, subnet, task_type, start_port, end_port):
	# mater_tasks
	db = MySQLdb.connect(host=mysql_host,
	                     user="root",
	                     passwd="123",
	                     db="test")

	cursor = db.cursor()

	cursor.execute("INSERT INTO `master_tasks` (`ip_address`,`subnet`, `task_type`, `start_port`,`end_port`) \
		VALUES(%s, %s, %s, %s, %s)", (ip, subnet, task_type, start_port, end_port))
	
	masterTaskId = cursor.lastrowid

	db.commit()
	db.close()

	return masterTaskId

def dataMapper(row):
	result = {}
	
	try:
		scan_result = pickle.loads(row[1])
		scan_result = list(filter(lambda host : host['status'] == 'open' or host['status'] == 'alive', scan_result))
		result['scan_result'] = scan_result
	except:
		result['scan_result'] = []
	
	result['task_status'] = row[0]
	result['date_done'] = str(row[2])
	result['master_task_id'] = row[3]

	return result

def get_results():
	# Connect
	db = MySQLdb.connect(host=mysql_host,
	                     user="root",
	                     passwd="123",
	                     db="test")

	cursor = db.cursor()

	cursor.execute("SELECT * from master_tasks")
	master_resultSet = cursor.fetchall()
	
	aggregate_result = {}
	
	for master_result in master_resultSet:
		temp =  aggregate_result.setdefault(master_result[0],{})
		temp['ip_address'] = master_result[1]
		temp['start_port'] = master_result[2]
		temp['end_port'] = master_result[3]
		temp['subnet'] = master_result[4]
		if master_result[5] == 'normal_scan':
			temp['task_type'] = "Normal Scan"
		elif master_result[5] == 'ping_scan':
			temp['task_type'] = "Ping Scan"
		elif master_result[5] == 'syn_scan':
			temp['task_type'] = "SYN Scan"
		elif master_result[5] == 'fyn_scan':
			temp['task_type'] = "FIN Scan"
		
	cursor.execute("SELECT `celery_taskmeta`.status, \
		`celery_taskmeta`.result, `celery_taskmeta`.date_done,\
		`celery_tasks`.master_task_id, `master_tasks`.task_type \
		FROM \
		`master_tasks` INNER JOIN `celery_tasks` \
		ON `master_tasks`.id = `celery_tasks`.master_task_id\
		INNER JOIN `celery_taskmeta`  \
		ON `celery_taskmeta`.task_id = `celery_tasks`.task_id")
	
	resultSet = cursor.fetchall()

	results = list(map(dataMapper,resultSet)) 
	results = list(filter(lambda row : len(row) > 0, results))
	
	for result in results:
		master_task_id = result['master_task_id']
		temp =  aggregate_result[master_task_id]
		current_open_hosts = temp.setdefault("open_hosts",[])
		temp["open_hosts"] = current_open_hosts + result["scan_result"]
		
	db.close()

	return aggregate_result