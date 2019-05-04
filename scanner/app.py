from flask import Flask, render_template, request
from scanner import syn_scan,fyn_scan,grab_banner, ping_scan
from db import get_results, create_master_task
import json
from utils import get_ip_range

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


# TODO : do input validation
@flask_app.route('/port_scan', methods=['POST'])
def port_scan_request():
	dest_ip = request.form['ip_address'] 
	network_prefix = request.form['network_prefix'] 
	start_port = int(request.form['start_port']) 
	end_port = int(request.form['end_port']) 
	scan_mode = request.form['scan_mode'] 
	
	address_list = get_ip_range(dest_ip, network_prefix) 

	# wrap in a try catch
	master_task_id = create_master_task(dest_ip, network_prefix, scan_mode, start_port, end_port)

	tasks = []
	for address in address_list:
		for port in range(start_port, end_port + 1):
			tasks.append((master_task_id, str(address),port))

	port_scanner = None
	
	# decide on a correct number currently set to 5
	if scan_mode == "normal_scan":
		port_scanner = grab_banner 
	elif scan_mode == "syn_scan":
		port_scanner = syn_scan
	elif scan_mode == "fyn_scan":
		port_scanner = fyn_scan 

	port_scanner.chunks(tasks, 5).apply_async()	
	
	return json.dumps({"status" : "OK"})