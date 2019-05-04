#!/usr/bin/python
import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb
import pickle


def associate_master_celery_task(master_task_id, task_id):
	db = MySQLdb.connect(host="127.0.0.1",
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
	db = MySQLdb.connect(host="127.0.0.1",
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
		pass
	
	result['task_status'] = row[0]
	result['date_done'] = str(row[2])
	result['master_task_id'] = row[3]
	result['task_type'] = row[4]

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
		`celery_tasks`.master_task_id, `master_tasks`.task_type \
		FROM \
		`master_tasks` INNER JOIN `celery_tasks` \
		ON `master_tasks`.id = `celery_tasks`.master_task_id\
		INNER JOIN `celery_taskmeta`  \
		ON `celery_taskmeta`.task_id = `celery_tasks`.task_id")
	
	resultSet = cursor.fetchall()

	results = list(map(dataMapper,resultSet)) 
	results = list(filter(lambda row : len(row) > 0, results))

	aggregate_result = {}

	for result in results:
		master_task_id = result['master_task_id']
		temp =  aggregate_result.setdefault(master_task_id,{})
		current_open_hosts = temp.setdefault("open_hosts",[])
		temp["open_hosts"] = current_open_hosts + result["scan_result"]
		temp["task_type"] = result["task_type"]
		aggregate_result[master_task_id] = temp
		
	db.close()

	return aggregate_result