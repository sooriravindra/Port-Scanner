from flask import Flask, render_template, request
from scanner import syn_scan,fyn_scan,grab_banner, ping_scan
from db import get_results, create_master_task
import json
from utils import *

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/get_results')
def scan_results():
	results = get_results()	
	return json.dumps(results)

@app.route('/ping_scan', methods=['POST'])
def ping_scan_request():
	dest_ip = request.form['ip_address'] 
	network_prefix = request.form['network_prefix']

	if not validate_ip_address(dest_ip):
		return json.dumps({"status" : "ERROR", "message" : "Please enter a valid ip"})

	address_list = None
	master_task_id = None

	try:
		address_list = get_ip_range(dest_ip, network_prefix)
	except:
		return json.dumps({"status" : "ERROR", "message" : "Not a valid IP4 address"})
	
	try:
		master_task_id = create_master_task(dest_ip, network_prefix, "ping_scan", -1, -1)
	except:
		return json.dumps({"status" : "ERROR", "message" : "Database Error"})

	address_list = map(lambda address : (master_task_id, str(address)), address_list)
	ping_scan.chunks(address_list, 5).apply_async()	
	
	return json.dumps({"status" : "OK"})


@app.route('/port_scan', methods=['POST'])
def port_scan_request():
	
	dest_ip = request.form['ip_address']
	network_prefix = request.form['network_prefix']
	start_port = int_cast(request.form['start_port'])
	end_port = int_cast(request.form['end_port'])
	scan_mode = request.form['scan_mode'] 
	
	if not validate_ip_address(dest_ip):
		return json.dumps({"status" : "ERROR", "message" : "Please enter a valid ip"})

	if not validate_port(start_port):
		return json.dumps({"status" : "ERROR", "message" : "Please enter a valid start port"})

	if not validate_port(end_port):
		return json.dumps({"status" : "ERROR", "message" : "Please enter a valid end port"})

	port_scanner = None
	
	# decide on a correct number currently set to 5
	if scan_mode == "normal_scan":
		port_scanner = grab_banner 
	elif scan_mode == "syn_scan":
		port_scanner = syn_scan
	elif scan_mode == "fyn_scan":
		port_scanner = fyn_scan
	else:
		return json.dumps({"status" : "ERROR", "message" : "The scan mode is invalid."})

	address_list = None
	master_task_id = None

	try:
		address_list = get_ip_range(dest_ip, network_prefix)
	except:
		return json.dumps({"status" : "ERROR", "message" : "Not a valid IP4 address"})
	
	try:
		master_task_id = create_master_task(dest_ip, network_prefix, scan_mode, start_port, end_port)
	except:
		return json.dumps({"status" : "ERROR", "message" : "Database Error"})
	

	tasks = []
	for address in address_list:
		for port in range(start_port, end_port + 1):
			tasks.append((master_task_id, str(address),port))

	port_scanner.chunks(tasks, 5).apply_async()	
	
	return json.dumps({"status" : "OK"})