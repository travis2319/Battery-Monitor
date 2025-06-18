class Config:
    CHECK_INTERVAL = 60  # in seconds
    LOW_BATTERY_THRESHOLD = 30  # %
    CRITICAL_BATTERY_THRESHOLD = 15  # %
    BATTERY_HEALTH_THRESHOLD = 95  # %
    ALERT_EMAIL = 'pdarryl@trellissoft.ai,ftravis@trellissoft.ai'
    ALERT_COOLDOWN_MINUTES = 15
    WEB_PORT = 8081

    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = 'pereiradarryl9@gmail.com'
    SMTP_PASSWORD = 'lfpewgctbwovalpt'
    USE_TLS = True


# #!/usr/bin/env python3
# """
# Configuration file for Battery Monitor
# """

# class Config:
#     # Web server settings
#     WEB_PORT = 8081
    
#     # Battery monitoring settings
#     CHECK_INTERVAL = 60  # seconds between battery checks
    
#     # Alert thresholds
#     LOW_BATTERY_THRESHOLD = 20        # % - Send warning at 20%
#     CRITICAL_BATTERY_THRESHOLD = 10   # % - Send critical alert at 10%
#     BATTERY_HEALTH_THRESHOLD = 95     # % - Alert if battery health drops below 95%
    
#     # Alert settings
#     ALERT_EMAIL = "travisfernandes2327@gmail.com"
#     ALERT_COOLDOWN_MINUTES = 30  # Minutes between same type of alerts
    
#     # Email settings
#     FROM_EMAIL = "pereiradarryl9@gmail.com"
#     SMTP_HOST = "smtp.gmail.com"
#     SMTP_PORT = 587
#     SMTP_USERNAME = "pereiradarryl9@gmail.com"
#     SMTP_PASSWORD = "lfpewgctbwovalpt"  # Consider using environment variable
    
#     # System settings
#     BATTERY_PATH = "/sys/class/power_supply"
    
#     @classmethod
#     def get_alert_conditions(cls):
#         """Get human-readable alert conditions"""
#         return {
#             'low_battery': f"Battery level drops to {cls.LOW_BATTERY_THRESHOLD}% or below",
#             'critical_battery': f"Battery level drops to {cls.CRITICAL_BATTERY_THRESHOLD}% or below",
#             'battery_health': f"Battery health drops below {cls.BATTERY_HEALTH_THRESHOLD}%",
#             'not_charging': "AC adapter connected but battery not charging",
#             'cooldown_period': f"Minimum {cls.ALERT_COOLDOWN_MINUTES} minutes between same alert types"
#         }