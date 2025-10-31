#!/usr/bin/env python3
"""
LoRa Device Diagnostic Tool
Tests device detection and monitoring without the display
"""

import glob
import subprocess
import time

def find_serial_devices():
    """Find all serial devices"""
    print("=" * 50)
    print("SERIAL DEVICE SCAN")
    print("=" * 50)
    
    usb_devices = glob.glob('/dev/ttyUSB*')
    acm_devices = glob.glob('/dev/ttyACM*')
    all_devices = sorted(usb_devices + acm_devices)
    
    if not all_devices:
        print("âŒ No serial devices found!")
        print("\nTroubleshooting:")
        print("1. Check USB cable connections")
        print("2. Run 'lsusb' to see if device is detected")
        print("3. Check dmesg for device errors: dmesg | tail -30")
        return []
    
    print(f"âœ“ Found {len(all_devices)} device(s):\n")
    
    for device in all_devices:
        print(f"ðŸ“¡ {device}")
        
        # Try to get device info with udevadm
        try:
            result = subprocess.run(
                ['udevadm', 'info', '--name', device],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Extract useful info
                for line in result.stdout.split('\n'):
                    if 'ID_VENDOR=' in line or 'ID_MODEL=' in line or 'ID_SERIAL=' in line:
                        print(f"   {line.strip()}")
        except Exception as e:
            print(f"   (Could not get device info: {e})")
        
        # Check permissions
        try:
            with open(device, 'r'):
                print(f"   âœ“ Read access OK")
        except PermissionError:
            print(f"   âŒ Permission denied! Add user to 'dialout' group:")
            print(f"      sudo usermod -a -G dialout $USER")
        except:
            pass
        
        print()
    
    return all_devices

def check_reticulum():
    """Check Reticulum status"""
    print("=" * 50)
    print("RETICULUM STATUS")
    print("=" * 50)
    
    # Check if rnsd service is running
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'rnsd'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.stdout.strip() == 'active':
            print("âœ“ rnsd service is ACTIVE")
        else:
            print(f"âŒ rnsd service is {result.stdout.strip().upper()}")
            print("   Start it with: sudo systemctl start rnsd")
    except Exception as e:
        print(f"âŒ Could not check rnsd: {e}")
    
    # Try to get rnstatus
    print("\nTrying to query Reticulum status...")
    try:
        result = subprocess.run(
            ['rnstatus'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("âœ“ Reticulum is responding")
            print("\nOutput:")
            print(result.stdout)
        else:
            print("âŒ rnstatus returned error")
            print(result.stderr)
    except FileNotFoundError:
        print("âŒ rnstatus command not found!")
        print("   Is Reticulum installed?")
    except Exception as e:
        print(f"âŒ Error: {e}")
    
    print()

def monitor_activity(devices, duration=10):
    """Monitor devices for activity"""
    if not devices:
        print("No devices to monitor!")
        return
    
    print("=" * 50)
    print(f"MONITORING ACTIVITY ({duration}s)")
    print("=" * 50)
    print("Watching for data on serial devices...")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        for i in range(duration):
            for device in devices:
                # Check if device is being used
                try:
                    result = subprocess.run(
                        ['lsof', device],
                        capture_output=True,
                        timeout=1
                    )
                    
                    if result.returncode == 0:
                        # Device is open
                        processes = result.stdout.decode().strip().split('\n')[1:]
                        if processes and processes[0]:
                            process_info = processes[0].split()
                            print(f"ðŸ“¡ {device}: ACTIVE (used by {process_info[0]})")
                    else:
                        print(f"âšª {device}: idle")
                except:
                    print(f"âšª {device}: unknown")
            
            time.sleep(1)
            if i < duration - 1:
                print()
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def main():
    print("\n" + "="*50)
    print("ðŸ”§ LoRa Device Diagnostic Tool")
    print("="*50 + "\n")
    
    # Find devices
    devices = find_serial_devices()
    
    # Check Reticulum
    check_reticulum()
    
    # Optionally monitor
    if devices:
        print("\nWould you like to monitor device activity? (y/n): ", end='')
        # For script automation, we'll skip this and just show we can
        print("\n(Skipping in automated mode)\n")
        # Uncomment below for interactive use:
        # response = input().lower()
        # if response == 'y':
        #     monitor_activity(devices)

if __name__ == '__main__':
    main()
