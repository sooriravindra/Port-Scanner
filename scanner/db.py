#!/usr/bin/python
import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb
import pickle

def create_master_task(ip, subnet, start_port, end_port):
	# mater_tasks
	db = MySQLdb.connect(host="127.0.0.1",
	                     user="root",
	                     passwd="123",
	                     db="test")

	cursor = db.cursor()

	# Execute SQL select statement
	cursor.execute("INSERT INTO `master_tasks` (`ip_address`,`subnet`, `start_port`,`end_port`) \
		VALUES(%s, %s, %s, %s)", (ip, subnet, start_port, end_port))
	
	masterTaskId = cursor.lastrowid

	db.commit()
	db.close()

	return masterTaskId

def dataMapper(row):
	result = {}
	
	try:
		scan_result = pickle.loads(row[1])
		scan_result = list(filter(lambda host : host['status'] == 'open', scan_result))
		result['scan_result'] = scan_result
	except:
		return []
	
	result['task_status'] = row[0]
	result['date_done'] = str(row[2])
	result['task_name'] = row[3]
	result['master_task_id'] = row[4]

	return result

def get_results():
	# Connect
	db = MySQLdb.connect(host="127.0.0.1",
	                     user="root",
	                     passwd="123",
	                     db="test")

	cursor = db.cursor()

	cursor.execute("SELECT `celery_taskmeta`.status, \
		`celery_taskmeta`.result, `celery_taskmeta`.date_done,\
		`celery_tasks`.task_name, `celery_tasks`.master_task_id \
		FROM \
		`celery_taskmeta` INNER JOIN `celery_tasks` \
		on `celery_taskmeta`.task_id = `celery_tasks`.task_id")
	
	resultSet = cursor.fetchall()


	results = list(map(dataMapper,resultSet)) 
	results = list(filter(lambda row : len(row) > 0, results))

	aggregate_result = {}

	for result in results:
		master_task_id = result['master_task_id']
		current_open_hosts = aggregate_result.setdefault(master_task_id,[])
		aggregate_result[master_task_id] = current_open_hosts + result["scan_result"]
		
	db.close()

	return aggregate_result