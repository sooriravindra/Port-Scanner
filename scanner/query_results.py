#!/usr/bin/python
import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb

def get_report():
	# Connect
	db = MySQLdb.connect(host="127.0.0.1",
	                     user="root",
	                     passwd="123",
	                     db="test")

	cursor = db.cursor()

	# Execute SQL select statement
	cursor.execute("SELECT * FROM celery_tasks")
	
	result_set = cursor.fetchall()
	
	# Close the connection
	db.close()

	return result_set
