from flask import Flask, render_template, request
from scanner import syn_scan,fyn_scan,grab_banner, ping_scan
from db import get_results, create_master_task
import json
from utils import get_ip_range
import re

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
	return render_template('index.html')

@flask_app.route('/get_results')
def scan_results():
	results = get_results()	
	return json.dumps(results)

# TODO : validation
@flask_app.route('/ping_scan', methods=['POST'])
def ping_scan_request():
	dest_ip = request.form['ip_address'] 
	network_prefix = request.form['network_prefix']

	master_task_id = create_master_task(dest_ip, network_prefix, "ping_scan", -1, -1)

	address_list = get_ip_range(dest_ip, network_prefix)
	address_list = map(lambda address : (master_task_id, str(address)), address_list)
	ping_scan.chunks(address_list, 5).apply_async()	
	
	return json.dumps({"status" : "OK"})

def int_cast(val):
	try:
		val = int(val)
	except:
		return -1
	return val

@flask_app.route('/port_scan', methods=['POST'])
def port_scan_request():
	dest_ip = request.form['ip_address']
	matchObj = re.match( r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', dest_ip, re.M)
	if not matchObj:
	   return json.dumps({"status" : "The IP Address provided is invalid."})
	network_prefix = request.form['network_prefix']
	start_port = int_cast(request.form['start_port'])
	if start_port < 0 or start_port > 65535:
		return json.dumps({"status" : "The starting port is invalid."})
	end_port = int_cast(request.form['end_port'])
	if end_port < 0 or end_port > 65535:
		return json.dumps({"status" : "The ending port is invalid."})
	scan_mode = request.form['scan_mode'] 
	port_scanner = None
	
	# decide on a correct number currently set to 5
	if scan_mode == "normal_scan":
		port_scanner = grab_banner 
	elif scan_mode == "syn_scan":
		port_scanner = syn_scan
	elif scan_mode == "fyn_scan":
		port_scanner = fyn_scan
	else:
		return json.dumps({"status" : "The scan mode is invalid."})


	address_list = get_ip_range(dest_ip, network_prefix) 

	# wrap in a try catch
	master_task_id = create_master_task(dest_ip, network_prefix, scan_mode, start_port, end_port)
	print("finished create_master_task")

	tasks = []
	for address in address_list:
		for port in range(start_port, end_port + 1):
			tasks.append((master_task_id, str(address),port))

	port_scanner.chunks(tasks, 5).apply_async()	
	
	return json.dumps({"status" : "OK"})