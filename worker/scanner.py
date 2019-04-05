#! /usr/bin/env python3

from scapy.all import *

def syn_scan(dest_ip, dport,timeout):
    
    sport = RandShort()
    
    response = sr1( IP(dst=dest_ip) /TCP(sport=sport,dport=dport,flags="S"),timeout=timeout)
    
    if(str(type(response))=="<type 'NoneType'>"):
        return 0

    elif(response.haslayer(TCP)):
        if(response.getlayer(TCP).flags == 0x12):
            i = send(IP(dst=dest_ip)/TCP(sport=sport,dport=dport,flags="R"))
            return 1

        elif (response.getlayer(TCP).flags == 0x14):
            return 0
   
    return -1

def launch_scans():
    dest_ip = '45.33.32.156'
    dport = 21
    timeout = 5
    scan_result = syn_scan(dport=dport, dest_ip=dest_ip, timeout=timeout)
    return scan_result
