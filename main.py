#!/usr/bin/env python3
"""
Battery Status Monitor for Proxmox System
Main application file
"""

import os
import sys
import time
import logging
import threading
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from battery_checker import BatteryChecker
from email_notifier import EmailNotifier
from config import Config

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Setup logger
logger = logging.getLogger('battery_monitor')
logger.setLevel(logging.INFO)

# Timed rotating file handler — rotates daily, keeps 7 days
file_handler = TimedRotatingFileHandler(
    'logs/battery_monitor.log',
    when='D',             # D = daily
    interval=1,           # every 1 day
    backupCount=7         # keep last 7 log files
)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Stream handler (console output)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Example log entry
logger.info("Battery Monitor application started.")

class BatteryMonitorApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.battery_checker = BatteryChecker()
        self.email_notifier = EmailNotifier()
        self.current_status = {}
        self.alert_history = []
        self.last_alert_time = {}
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/battery-status')
        def get_battery_status():
            return jsonify(self.current_status)
        
        @self.app.route('/api/alert-history')
        def get_alert_history():
            return jsonify(self.alert_history[-50:])  # Last 50 alerts
        
        @self.app.route('/api/send-mail', methods=['GET'])
        def send_mail():
            subject = request.args.get('subject', 'Test Subject')
            message = request.args.get('message', 'Test Message')
            success = self.send_alert(subject, message)
            return jsonify({
                'subject': subject,
                'message': message,
                'sent': success
            })
    
    def check_battery_and_alert(self):
        """Background thread to monitor battery and send alerts"""
        while True:
            try:
                # Get battery status
                status = self.battery_checker.get_battery_status()
                self.current_status = status
                
                # Check for alert conditions
                self.check_alert_conditions(status)
                
                # Wait before next check
                time.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in battery monitoring: {e}")
                time.sleep(30)  # Wait 30 seconds on error
    
    def check_alert_conditions(self, status):
        """Check if we need to send alerts based on battery status"""
        current_time = datetime.now()
        
        # Low battery alert
        if status['percentage'] <= Config.LOW_BATTERY_THRESHOLD and not status['ac_connected']:
            if self.should_send_alert('low_battery', current_time):
                self.send_alert(
                    'Low Battery Warning',
                    f"Battery level is critically low: {status['percentage']}%\n"
                    f"Status: {status['status']}\n"
                    f"Time remaining: {status['time_remaining']}"
                )
                self.last_alert_time['low_battery'] = current_time
        
        # Critical battery alert
        if status['percentage'] <= Config.CRITICAL_BATTERY_THRESHOLD and not status['ac_connected']:
            if self.should_send_alert('critical_battery', current_time):
                self.send_alert(
                    'CRITICAL Battery Alert',
                    f"Battery level is CRITICALLY low: {status['percentage']}%\n"
                    f"Status: {status['status']}\n"
                    f"Time remaining: {status['time_remaining']}\n"
                    f"IMMEDIATE ACTION REQUIRED!"
                )
                self.last_alert_time['critical_battery'] = current_time
        
        # Battery not charging alert (when plugged in)
        if status['ac_connected'] and status['status'] == 'Not charging':
            if self.should_send_alert('not_charging', current_time):
                self.send_alert(
                    'Battery Not Charging',
                    f"AC adapter is connected but battery is not charging.\n"
                    f"Current level: {status['percentage']}%\n"
                    f"Status: {status['status']}\n"
                    f"Please check power adapter and battery health."
                )
                self.last_alert_time['not_charging'] = current_time
        
        # Battery health alert
        if status['percentage'] < Config.BATTERY_HEALTH_THRESHOLD and not status['ac_connected']:
            if self.should_send_alert('battery_health', current_time):
                self.send_alert(
                    'Battery Health Warning',
                    f"Battery health has degraded: {status['health']}%\n"
                    f"Current level: {status['percentage']}%\n"
                    f"Consider replacing the battery soon."
                )
                self.last_alert_time['battery_health'] = current_time
    
    def should_send_alert(self, alert_type, current_time):
        """Check if enough time has passed since last alert of this type"""
        if alert_type not in self.last_alert_time:
            return True
        
        time_since_last = current_time - self.last_alert_time[alert_type]
        return time_since_last >= timedelta(minutes=Config.ALERT_COOLDOWN_MINUTES)
    
    def send_alert(self, subject, message):
        """Send email alert and log it"""
        try:
            full_message = f"""
Battery Monitor Alert - Proxmox System

{message}

System Information:
- Hostname: {os.uname().nodename}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Uptime: {self.get_system_uptime()}

This is an automated alert from the Proxmox battery monitoring system.
"""
            
            success = self.email_notifier.send_email(
                Config.ALERT_EMAIL,
                subject,
                full_message
            )
            
            alert_record = {
                'timestamp': datetime.now().isoformat(),
                'subject': subject,
                'message': message,
                'sent': success
            }
            
            self.alert_history.append(alert_record)
            
            if success:
                logger.info(f"Alert sent successfully: {subject}")
            else:
                logger.error(f"Failed to send alert: {subject}")
                
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_system_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_hours = int(uptime_seconds // 3600)
                uptime_minutes = int((uptime_seconds % 3600) // 60)
                return f"{uptime_hours}h {uptime_minutes}m"
        except:
            return "Unknown"
    
    def run(self):
        """Start the application"""
        logger.info("Starting Battery Monitor Application")
        
        # Start background monitoring thread
        monitor_thread = threading.Thread(target=self.check_battery_and_alert, daemon=True)
        monitor_thread.start()
        
        # Start Flask web server
        self.app.run(
            host='0.0.0.0',
            port=Config.WEB_PORT,
            debug=False,
            threaded=True
        )

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    
    # Start the application
    app = BatteryMonitorApp()
    app.run()