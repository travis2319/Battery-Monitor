#!/usr/bin/env python3
"""
Email Test Script using msmtp configuration
Tests email sending functionality with your msmtp settings
"""

import smtplib
import subprocess
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuration from your msmtp settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = "pereiradarryl9@gmail.com"
TO_EMAIL = "travisfernandes2327@gmail.com"
USERNAME = "pereiradarryl9@gmail.com"
PASSWORD = "lfpewgctbwovalpt"

def test_with_python_smtplib():
    """Test email sending using Python's built-in smtplib"""
    print("Testing with Python smtplib...")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL  # Send to yourself for testing
        msg['Subject'] = f"Test Email - Python smtplib - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = """
        This is a test email sent using Python's smtplib.
        
        Test details:
        - SMTP Host: smtp.gmail.com
        - Port: 587
        - TLS: Enabled
        - Authentication: Enabled
        
        If you receive this email, your configuration is working correctly!
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()  # Enable TLS
        server.login(USERNAME, PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, TO_EMAIL, text)
        server.quit()
        
        print("✅ Email sent successfully using Python smtplib!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email using Python smtplib: {e}")
        return False

def test_with_msmtp():
    """Test email sending using msmtp command"""
    print("\nTesting with msmtp command...")
    
    try:
        # Create email content
        email_content = f"""To: {FROM_EMAIL}
From: {TO_EMAIL}
Subject: Test Email - msmtp - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test email sent using msmtp.

Test details:
- Configuration file: ~/.msmtprc (or system config)
- Account: gmail
- Host: smtp.gmail.com
- Port: 587
- TLS: Enabled

If you receive this email, your msmtp configuration is working correctly!
"""
        
        # Run msmtp command
        process = subprocess.run(
            ['msmtp', FROM_EMAIL],
            input=email_content,
            text=True,
            capture_output=True
        )
        
        if process.returncode == 0:
            print("✅ Email sent successfully using msmtp!")
            return True
        else:
            print(f"❌ Failed to send email using msmtp:")
            print(f"Error: {process.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ msmtp command not found. Make sure msmtp is installed.")
        return False
    except Exception as e:
        print(f"❌ Failed to send email using msmtp: {e}")
        return False

def check_msmtp_config():
    """Check if msmtp configuration is properly set up"""
    print("Checking msmtp configuration...")
    
    try:
        # Test msmtp configuration
        process = subprocess.run(
            ['msmtp', '--serverinfo', '--host=smtp.gmail.com', '--port=587'],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            print("✅ msmtp can connect to Gmail SMTP server")
            print("Server info:")
            print(process.stdout)
        else:
            print("❌ msmtp connection test failed:")
            print(process.stderr)
            
    except FileNotFoundError:
        print("❌ msmtp command not found")
    except Exception as e:
        print(f"❌ Error checking msmtp config: {e}")

def main():
    print("Email Configuration Test")
    print("=" * 40)
    print(f"Testing email functionality for: {FROM_EMAIL}")
    print(f"SMTP Server: {SMTP_HOST}:{SMTP_PORT}")
    print("=" * 40)
    
    # Check msmtp configuration
    check_msmtp_config()
    print()
    
    # Test with Python smtplib
    python_success = test_with_python_smtplib()
    
    # Test with msmtp
    msmtp_success = test_with_msmtp()
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print(f"Python smtplib: {'✅ PASS' if python_success else '❌ FAIL'}")
    print(f"msmtp command:  {'✅ PASS' if msmtp_success else '❌ FAIL'}")
    
    if python_success or msmtp_success:
        print("\n🎉 At least one method worked! Check your email inbox.")
    else:
        print("\n⚠️  Both methods failed. Please check your configuration.")
        print("\nTroubleshooting tips:")
        print("1. Verify your Gmail app password is correct")
        print("2. Ensure 2FA is enabled on your Gmail account")
        print("3. Check if 'Less secure app access' is disabled (should be)")
        print("4. Verify msmtp is installed: sudo apt install msmtp")
        print("5. Check msmtp config file location: ~/.msmtprc")

if __name__ == "__main__":
    main()