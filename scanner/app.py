from flask import Flask, render_template, request
from scanner import syn_scan,fyn_scan,grab_banner
from query_results import get_report
import json

# initialize Flask
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
	return render_template('index.html')

@flask_app.route('/get_results')
def get_results():
	# searchword = request.args.get('key', '')
	report = get_report()	
	return json.dumps(report)

@flask_app.route('/submit_task', methods=['POST'])
def submit_task():
	dest_ip = request.form['ip_address'] 
	network_prefix = request.form['network_prefix'] 
	start_port = int(request.form['start_port']) 
	end_port = int(request.form['end_port']) 
	scan_mode = request.form['scan_mode'] 
	grab_banner.delay('45.33.32.156', 80)
	return json.dumps({"status" : "OK"})