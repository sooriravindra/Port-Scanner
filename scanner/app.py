from flask import Flask, render_template, request
from scanner import syn_scan,fyn_scan,grab_banner
from query_results import get_results
import json
import ipaddress

# initialize Flask
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
	return render_template('index.html')

@flask_app.route('/get_results')
def scan_results():
	# searchword = request.args.get('key', '')
	results = get_results()	
	return json.dumps(results)

# TODO : do input validation
@flask_app.route('/submit_task', methods=['POST'])
def submit_task():
	dest_ip = request.form['ip_address'] 
	network_prefix = request.form['network_prefix'] 
	start_port = int(request.form['start_port']) 
	end_port = int(request.form['end_port']) 
	scan_mode = request.form['scan_mode'] 
	
	if not network_prefix or not network_prefix.strip():
		network_prefix = "32"

	full_address = "{}/{}".format(dest_ip,network_prefix)
	address_list = ipaddress.ip_network(full_address)

	# not the most ideal way of splitting; can pool ips and ports; 
	# but think about how to retrieve them while showing it to the user
	for address in address_list:
		for port in range(start_port, end_port + 1):
			grab_banner.delay(str(address), port)

	return json.dumps({"status" : "OK"})