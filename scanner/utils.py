import ipaddress

def get_ip_range(dest_ip, network_prefix):

	if not network_prefix or not network_prefix.strip():
		network_prefix = "32"

	full_address = "{}/{}".format(dest_ip,network_prefix)
	return ipaddress.ip_network(full_address)

