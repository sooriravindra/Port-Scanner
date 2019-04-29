#!/usr/bin/python
import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb
import pickle
import json

def dataMapper(row):
	result = {}
	result['id'] = row[0]
	result['task_id'] = row[1]
	result['status'] = row[2]
	result['result'] = json.loads(pickle.loads(row[3]))
	result['date_done'] = str(row[4])
	result['task_name'] = row[5]
	result['ip'] = row[6]
	result['port'] = row[7]
	return result

def get_results():
	# Connect
	db = MySQLdb.connect(host="127.0.0.1",
	                     user="root",
	                     passwd="123",
	                     db="test")

	cursor = db.cursor()

	# Execute SQL select statement
	cursor.execute("SELECT `celery_taskmeta`.id, `celery_taskmeta`.task_id, \
		`celery_taskmeta`.status , `celery_taskmeta`.result, `celery_taskmeta`.date_done,\
		`celery_tasks`.task_name, `celery_tasks`.ip, `celery_tasks`.port \
		FROM \
		`celery_taskmeta` INNER JOIN `celery_tasks` \
		on `celery_taskmeta`.task_id = `celery_tasks`.task_id")
	
	resultSet = cursor.fetchall()

	results = list(map(dataMapper,resultSet)) 
	
	db.close()

	return results
