import ipaddress
import re 
import datetime

def get_current_time():
	now = datetime.datetime.now()
	return now.isoformat()

def get_ip_range(dest_ip, network_prefix):
	full_address = "{}/{}".format(dest_ip,network_prefix)
	return ipaddress.ip_network(full_address)

def validate_ip_address(ip):

	matchObj = re.match( r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', ip, re.M)
	
	if not matchObj:
		return False

	return True

def validate_port(port):
	if port < 0 or port > 65535:
		return False

	return True

def int_cast(val):
	try:
		val = int(val)
	except:
		return -1
	return val
