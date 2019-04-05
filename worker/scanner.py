#! /usr/bin/env python3

from scapy.all import *

# -1 is unanswered
# 1 is open
# 0 is closed
# URG = 0x20
# ACK = 0x10
# PSH = 0x08
# RST = 0x04
# SYN = 0x02
# FIN = 0x01

#SYN|ACK = 0x12
#ACK|RST = 0x14

def syn_scan(dest_ip, dport,timeout):
    
    sport = RandShort()
    
    response = sr1( IP(dst=dest_ip) /TCP(sport=sport,dport=dport,flags="S"),timeout=timeout)
    
    if response is not None:
        if(response.haslayer(TCP)):
            # if 20 then its closed; then the server responded with SYN|ACK
            if(response.getlayer(TCP).flags == 0x12):
                # send rst if the kernel fails to send
                i = send(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="R"))
                return 1
            # port is closed ACK|RST
            elif (response.getlayer(TCP).flags == 0x14):
                return 0
    else:
        return -1

# mode can syn scan, full banner
def start_scan(mode,dest_ip,dport,timeout):
    scan_result = -1
    if(mode  == 'syn_scan'):
        scan_result = syn_scan(dport=dport, dest_ip=dest_ip, timeout=timeout)

    return scan_result

