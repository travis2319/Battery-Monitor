#!/usr/bin/env python3
"""
Battery Checker Module
Handles reading battery information from the system
"""

import os
import re
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

class BatteryChecker:
    def __init__(self):
        self.battery_path = self.find_battery_path()
        
    def find_battery_path(self):
        """Find the battery path in /sys/class/power_supply/"""
        power_supply_path = "/sys/class/power_supply"
        
        if not os.path.exists(power_supply_path):
            logger.error("Power supply path not found")
            return None
            
        for item in os.listdir(power_supply_path):
            item_path = os.path.join(power_supply_path, item)
            type_file = os.path.join(item_path, "type")
            
            if os.path.exists(type_file):
                try:
                    with open(type_file, 'r') as f:
                        if f.read().strip() == "Battery":
                            logger.info(f"Found battery at: {item_path}")
                            return item_path
                except:
                    continue
                    
        logger.warning("No battery found in power supply")
        return None
    
    def read_battery_file(self, filename):
        """Read a battery information file"""
        if not self.battery_path:
            return None
            
        file_path = os.path.join(self.battery_path, filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.debug(f"Could not read {filename}: {e}")
        return None
    
    def get_ac_adapter_status(self):
        """Check if AC adapter is connected"""
        power_supply_path = "/sys/class/power_supply"
        
        if not os.path.exists(power_supply_path):
            return False
            
        for item in os.listdir(power_supply_path):
            if item.startswith(('ADP', 'AC', 'ACAD')):
                online_file = os.path.join(power_supply_path, item, "online")
                try:
                    if os.path.exists(online_file):
                        with open(online_file, 'r') as f:
                            return f.read().strip() == "1"
                except:
                    continue
        return False
    
    def get_battery_status(self):
        """Get comprehensive battery status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'battery_present': False,
            'percentage': 0,
            'status': 'Unknown',
            'health': 100,
            'voltage': 0,
            'current': 0,
            'temperature': 0,
            'time_remaining': 'Unknown',
            'ac_connected': False,
            'cycle_count': 0,
            'capacity_full': 0,
            'capacity_design': 0,
            'technology': 'Unknown',
            'manufacturer': 'Unknown',
            'model': 'Unknown'
        }
        
        # Check AC adapter
        status['ac_connected'] = self.get_ac_adapter_status()
        
        if not self.battery_path:
            logger.warning("No battery found")
            return status
        
        # Battery present
        present = self.read_battery_file("present")
        status['battery_present'] = present == "1" if present else False
        
        if not status['battery_present']:
            logger.warning("Battery not present")
            return status
        
        # Basic battery info
        capacity = self.read_battery_file("capacity")
        if capacity:
            status['percentage'] = int(capacity)
        
        battery_status = self.read_battery_file("status")
        if battery_status:
            status['status'] = battery_status
        
        # Voltage (convert from microvolts to volts)
        voltage = self.read_battery_file("voltage_now")
        if voltage:
            status['voltage'] = round(int(voltage) / 1000000, 2)
        
        # Current (convert from microamps to amps)
        current = self.read_battery_file("current_now")
        if current:
            status['current'] = round(int(current) / 1000000, 2)
        
        # Temperature (convert from tenths of degrees Celsius)
        temp = self.read_battery_file("temp")
        if temp:
            status['temperature'] = round(int(temp) / 10, 1)
        
        # Capacity information
        capacity_full = self.read_battery_file("charge_full")
        capacity_design = self.read_battery_file("charge_full_design")
        
        if capacity_full:
            status['capacity_full'] = int(capacity_full)
        if capacity_design:
            status['capacity_design'] = int(capacity_design)
        
        # Calculate health percentage
        if capacity_full and capacity_design:
            status['health'] = round((int(capacity_full) / int(capacity_design)) * 100, 1)
        
        # Cycle count
        cycle_count = self.read_battery_file("cycle_count")
        if cycle_count:
            status['cycle_count'] = int(cycle_count)
        
        # Technology
        technology = self.read_battery_file("technology")
        if technology:
            status['technology'] = technology
        
        # Manufacturer
        manufacturer = self.read_battery_file("manufacturer")
        if manufacturer:
            status['manufacturer'] = manufacturer
        
        # Model
        model = self.read_battery_file("model_name")
        if model:
            status['model'] = model
        
        # Calculate time remaining
        status['time_remaining'] = self.calculate_time_remaining(status)
        
        logger.debug(f"Battery status: {status['percentage']}% - {status['status']}")
        return status
    
    def calculate_time_remaining(self, status):
        """Calculate estimated time remaining"""
        try:
            if status['current'] == 0:
                return "Unknown"
            
            if status['status'] == 'Discharging':
                # Time until empty
                current_charge = self.read_battery_file("charge_now")
                if current_charge and status['current'] < 0:
                    hours = abs(int(current_charge) / (status['current'] * 1000000))
                    return f"{int(hours)}h {int((hours % 1) * 60)}m"
            
            elif status['status'] == 'Charging':
                # Time until full
                current_charge = self.read_battery_file("charge_now")
                if current_charge and status['capacity_full'] and status['current'] > 0:
                    remaining_charge = status['capacity_full'] - int(current_charge)
                    hours = remaining_charge / (status['current'] * 1000000)
                    return f"{int(hours)}h {int((hours % 1) * 60)}m"
            
            return "Unknown"
            
        except Exception as e:
            logger.debug(f"Error calculating time remaining: {e}")
            return "Unknown"
    
    def get_system_power_info(self):
        """Get additional system power information"""
        info = {}
        
        try:
            # Get system load
            with open('/proc/loadavg', 'r') as f:
                load = f.read().strip().split()
                info['load_average'] = f"{load[0]} {load[1]} {load[2]}"
        except:
            info['load_average'] = "Unknown"
        
        try:
            # Get CPU frequency
            result = subprocess.run(['cat', '/proc/cpuinfo'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                cpu_info = result.stdout
                mhz_match = re.search(r'cpu MHz\s*:\s*([\d.]+)', cpu_info)
                if mhz_match:
                    info['cpu_frequency'] = f"{float(mhz_match.group(1)):.0f} MHz"
        except:
            info['cpu_frequency'] = "Unknown"
        
        return info