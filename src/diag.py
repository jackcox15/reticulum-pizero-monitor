#!/usr/bin/env python3

import glob
import psutil
import subprocess

##################################

def check_rnsd():
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'rnsd'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.stdout.strip() == 'active'
    except:
        return False


def check_lora():
    usb_devices = glob.glob('/dev/ttyUSB*')
    acm_devices = glob.glob('/dev/ttyACM*')
    
    # If either list has items, device is connected
    return len(usb_devices) > 0 or len(acm_devices) > 0

#####################################

def get_rnstatus():
    try:
        result = subprocess.run(
            ['rnstatus'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except:
        return None

#####################################
    
def parse_traffic(rnstatus_output):

    if rnstatus_output is None:
        return None
    
    try:
        lines = rnstatus_output.split('\n')
        tx_bps = 0
        rx_bps = 0
        
        for i, line in enumerate(lines):
            if 'Traffic' in line and '↑' in line:
                # This line has upload (TX) info
                parts = line.split()
                for j, part in enumerate(parts):
                    if 'bps' in part and j > 0:
                        tx_bps = int(parts[j-1])
                        break
                
                # Next line should have download (RX)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if '↓' in next_line:
                        parts = next_line.split()
                        for j, part in enumerate(parts):
                            if 'bps' in part and j > 0:
                                rx_bps = int(parts[j-1])
                                break
                break
        
        return {
            'tx_bps': tx_bps,
            'rx_bps': rx_bps
        }
    except:
        return None

##########################################
def check_wifi():

    try:
        result = subprocess.run(
            ['ip', 'link', 'show', 'wlan0'],
            capture_output=True,
            text=True,
            timeout=2
        )
        # If command succeeds and output contains "UP"
        return result.returncode == 0 and 'UP' in result.stdout
    except:
        return False

############################################
    
def get_active_interfaces():
    try:
        net_stats = psutil.net_if_stats()
        active = []
        
        for interface, stats in net_stats.items():
            if interface == 'lo':
                continue
            if stats.isup:
                active.append(interface)
        return active
    except:
        return []
    
def get_interface_traffic(interface_name):
    try:
        net_io = psutil.net_io_counters(pernic=True)
        
        if interface_name in net_io:
            stats = net_io[interface_name]
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv
            }
        else:
            return None
    except:
        return None
