#!/usr/bin/env python3
#Service Monitor for rnsd, wifi, and LoRa USB connections

import subprocess
import os

def check_rnsd():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'rnsd'],
                                capture_output=True, text=True)
        is_running = (result.stdout.strip() == 'active')
        return is_running
    except:
        return False

def check_lora():
    if os.path.exists('/dev/ttyUSB0'):
        return True
    return False

def check_wifi():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'hostapd'],
                                 capture_output=True, text=True)
        is_running = (result.stdout.strip() == 'active')
        return is_running
    except:
        return False
    
    
    
    
    
    
if __name__ == '__main__':
    print("Testing services...")
    print(f"RNSD running: {check_rnsd()}")
    print(f"LoRa connected: {check_lora()}")
    print(f"Wifi AP active: {check_wifi()}")
