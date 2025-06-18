import smtplib
from email.message import EmailMessage
import logging
from config import Config

logger = logging.getLogger(__name__)

class EmailNotifier:
    def send_email(self, to_email, subject, body):
        try:
            msg = EmailMessage()
            msg['From'] = Config.SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.set_content(body)

            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                if Config.USE_TLS:
                    server.starttls()
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


# import os
# import logging
# import subprocess
# import tempfile
# import smtplib
# from datetime import datetime
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# logger = logging.getLogger(__name__)

# class EmailNotifier:
#     def __init__(self):
#         self.msmtp_path = self.find_msmtp()
#         self.config_file = os.path.expanduser("~/.msmtprc")
#         self.from_email = "pereiradarryl9@gmail.com"
        
#         # SMTP configuration for fallback
#         self.smtp_host = "smtp.gmail.com"
#         self.smtp_port = 587
#         self.smtp_username = "pereiradarryl9@gmail.com"
#         self.smtp_password = "lfpewgctbwovalpt"  # Consider using environment variable

#     def find_msmtp(self):
#         """Find msmtp executable"""
#         for path in ['/usr/bin/msmtp', '/usr/local/bin/msmtp', '/bin/msmtp']:
#             if os.path.exists(path):
#                 return path
#         try:
#             result = subprocess.run(['which', 'msmtp'], capture_output=True, text=True, timeout=5)
#             if result.returncode == 0:
#                 return result.stdout.strip()
#         except Exception as e:
#             logger.error(f"Error finding msmtp: {e}")
#         logger.warning("msmtp not found, will use smtplib fallback")
#         return None

#     def check_config(self):
#         """Check if msmtp configuration exists"""
#         if not os.path.exists(self.config_file):
#             logger.warning(f"msmtp config file not found: {self.config_file}")
#             return False
#         stat_info = os.stat(self.config_file)
#         if stat_info.st_mode & 0o077:
#             logger.warning(f"msmtp config file has unsafe permissions: {oct(stat_info.st_mode)}")
#         return True

#     def send_email_with_smtplib(self, to_email, subject, message):
#         """Send email using Python's built-in smtplib"""
#         try:
#             # Create message
#             msg = MIMEMultipart()
#             msg['From'] = self.from_email
#             msg['To'] = to_email
#             msg['Subject'] = f"[Proxmox-{os.uname().nodename}] {subject}"
            
#             # Create email body with same format as msmtp version
#             hostname = os.uname().nodename
#             email_body = f"""{message}

# --
# Proxmox Battery Monitor
# System: {hostname}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# """
            
#             msg.attach(MIMEText(email_body, 'plain'))
            
#             # Create SMTP session
#             server = smtplib.SMTP(self.smtp_host, self.smtp_port)
#             server.starttls()  # Enable TLS
#             server.login(self.smtp_username, self.smtp_password)
            
#             # Send email
#             text = msg.as_string()
#             server.sendmail(self.from_email, to_email, text)
#             server.quit()
            
#             logger.info(f"Email sent successfully to {to_email} using smtplib")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error sending email with smtplib: {e}")
#             return False

#     def send_email_with_msmtp(self, to_email, subject, message):
#         """Send email using msmtp"""
#         if not self.msmtp_path:
#             return False
            
#         try:
#             email_content = self.create_email_content(to_email, subject, message)
#             with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.eml') as tmp_file:
#                 tmp_file.write(email_content)
#                 tmp_file_path = tmp_file.name
#             os.chmod(tmp_file_path, 0o600)  # Secure permissions
            
#             try:
#                 # Try with specific account first, then fallback to default
#                 cmd = [self.msmtp_path, '--read-envelope-from', '--read-recipients']
                
#                 with open(tmp_file_path, 'r') as email_file:
#                     result = subprocess.run(
#                         cmd,
#                         stdin=email_file,
#                         capture_output=True,
#                         text=True,
#                         timeout=30
#                     )
                
#                 if result.returncode == 0:
#                     logger.info(f"Email sent successfully to {to_email} using msmtp")
#                     return True
#                 else:
#                     logger.warning(f"msmtp failed: {result.stderr.strip()}")
#                     return False
#             finally:
#                 os.unlink(tmp_file_path)
                
#         except subprocess.TimeoutExpired:
#             logger.error("Email sending with msmtp timed out")
#             return False
#         except Exception as e:
#             logger.error(f"Error sending email with msmtp: {e}")
#             return False

#     def send_email(self, to_email, subject, message):
#         """Send email using msmtp first, then fallback to smtplib"""
#         # Try msmtp first if available and configured
#         if self.msmtp_path and self.check_config():
#             logger.info("Attempting to send email using msmtp...")
#             if self.send_email_with_msmtp(to_email, subject, message):
#                 return True
#             logger.warning("msmtp failed, falling back to smtplib...")
#         else:
#             logger.info("msmtp not available or not configured, using smtplib...")
        
#         # Fallback to smtplib
#         return self.send_email_with_smtplib(to_email, subject, message)

#     def create_email_content(self, to_email, subject, message):
#         """Create properly formatted email content for msmtp"""
#         hostname = os.uname().nodename
#         return f"""From: Proxmox Battery Monitor <{self.from_email}>
# To: {to_email}
# Subject: [Proxmox-{hostname}] {subject}
# Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}
# Content-Type: text/plain; charset=UTF-8

# {message}

# --
# Proxmox Battery Monitor
# System: {hostname}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# """

#     def test_email_config(self):
#         """Send test email to verify setup"""
#         test_message = f"""This is a test email from the Proxmox Battery Monitor system.

# System: {os.uname().nodename}
# Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# msmtp Path: {self.msmtp_path}
# Config File: {self.config_file}
# Config Exists: {os.path.exists(self.config_file)}

# Email Method: {'msmtp + smtplib fallback' if self.msmtp_path else 'smtplib only'}"""
        
#         return self.send_email("travisfernandes2327@gmail.com", "Battery Monitor Test Email", test_message)

#     def get_status(self):
#         """Get detailed status of email configuration"""
#         return {
#             'msmtp_available': self.msmtp_path is not None,
#             'msmtp_path': self.msmtp_path,
#             'config_exists': os.path.exists(self.config_file),
#             'config_file': self.config_file,
#             'smtplib_available': True,
#             'smtp_host': self.smtp_host,
#             'smtp_port': self.smtp_port,
#             'primary_method': 'msmtp' if (self.msmtp_path and self.check_config()) else 'smtplib',
#             'fallback_available': True
#         }

#     def create_msmtp_config(self):
#         """Create a basic msmtp configuration file"""
#         config_content = f"""# msmtp configuration for Gmail
# defaults
# auth           on
# tls            on
# tls_trust_file /etc/ssl/certs/ca-certificates.crt
# logfile        ~/.msmtp.log

# # Gmail account
# account        gmail
# host           smtp.gmail.com
# port           587
# from           {self.from_email}
# user           {self.smtp_username}
# password       {self.smtp_password}

# # Set default account
# account default : gmail
# """
        
#         try:
#             with open(self.config_file, 'w') as f:
#                 f.write(config_content)
#             os.chmod(self.config_file, 0o600)  # Secure permissions
#             logger.info(f"Created msmtp configuration file: {self.config_file}")
#             return True
#         except Exception as e:
#             logger.error(f"Failed to create msmtp config: {e}")
#             return False

# # Example usage and test
# if __name__ == "__main__":
#     import sys
    
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
#     notifier = EmailNotifier()
    
#     print("Email Notifier Status:")
#     print("=" * 40)
#     status = notifier.get_status()
#     for key, value in status.items():
#         print(f"{key}: {value}")
    
#     print("\n" + "=" * 40)
#     print("Testing email functionality...")
    
#     if len(sys.argv) > 1 and sys.argv[1] == "create-config":
#         print("Creating msmtp configuration...")
#         if notifier.create_msmtp_config():
#             print("✅ msmtp configuration created successfully")
#         else:
#             print("❌ Failed to create msmtp configuration")
    
#     # Test email sending
#     success = notifier.test_email_config()
#     if success:
#         print("✅ Test email sent successfully!")
#     else:
#         print("❌ Failed to send test email")