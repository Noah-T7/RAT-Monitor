import subprocess
import datetime
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
ALERT_HOUR_START = 20  # 8 PM
ALERT_HOUR_END = 6     # 6 AM
SUSPICIOUS_PORTS = [4444, 1234, 5555, 8080]
LOG_FILE = "rat_alerts.txt"

# Email Configuration
EMAIL_SENDER = "thukunoah2@gmail.com"
EMAIL_RECEIVER = "thukunoah2@gmail.com"
EMAIL_PASSWORD =    "hurpjxywqxesfize"
EMAIL_ENABLED = True

def send_email_alert(subject, message):
    if not EMAIL_ENABLED:
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = f"🚨 SACCO Security Alert: {subject}"

        body = f"""
SACCO LOG MONITORING SYSTEM - SECURITY ALERT
=============================================

{message}

Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System: SACCO Banking Computer
Location: Murang'a County SACCO

---------------------------------------------
This is an automated alert from your SACCO Log Monitoring System.
Do NOT reply to this email.
Log into your dashboard at: http://saccomonitor.com:5000
        """

        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print(f"[EMAIL SENT] Alert email sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"[EMAIL ERROR] Could not send email: {str(e)}")

def log_alert(message, send_email=True, email_subject="Security Alert"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert = f"[ALERT] {timestamp} - {message}"
    print(alert)
    with open(LOG_FILE, "a") as f:
        f.write(alert + "\n")
    if send_email:
        send_email_alert(email_subject, message)

def check_suspicious_connections():
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        for port in SUSPICIOUS_PORTS:
            if f":{port}" in line and "ESTABLISHED" in line:
                log_alert(
                    f"Suspicious connection detected on port {port}: {line.strip()}",
                    send_email=True,
                    email_subject=f"RAT Connection Detected on Port {port}"
                )

def check_after_hours():
    current_hour = datetime.datetime.now().hour
    if current_hour >= ALERT_HOUR_START or current_hour < ALERT_HOUR_END:
        log_alert(
            f"After-hours activity detected at {datetime.datetime.now().strftime('%H:%M:%S')}",
            send_email=True,
            email_subject="After-Hours Activity Detected"
        )

def main():
    print("RAT Monitor Started - Monitoring for suspicious activity...")
    print(f"Alerts will be saved to: {os.path.abspath(LOG_FILE)}")
    print(f"Email alerts will be sent to: {EMAIL_RECEIVER}")
    print("Press Ctrl+C to stop\n")

    while True:
        check_suspicious_connections()
        check_after_hours()
        time.sleep(60)

if __name__ == "__main__":
    main()