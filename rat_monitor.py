import subprocess
import datetime
import time
import os

# Configuration
ALERT_HOUR_START = 20  # 8 PM
ALERT_HOUR_END = 6     # 6 AM
SUSPICIOUS_PORTS = [4444, 1234, 5555, 8080]
LOG_FILE = "rat_alerts.txt"

def log_alert(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert = f"[ALERT] {timestamp} - {message}"
    print(alert)
    with open(LOG_FILE, "a") as f:
        f.write(alert + "\n")

def check_suspicious_connections():
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        for port in SUSPICIOUS_PORTS:
            if f":{port}" in line and "ESTABLISHED" in line:
                log_alert(f"Suspicious connection detected on port {port}: {line.strip()}")

def check_after_hours():
    current_hour = datetime.datetime.now().hour
    if current_hour >= ALERT_HOUR_START or current_hour < ALERT_HOUR_END:
        log_alert(f"After-hours activity detected at {datetime.datetime.now().strftime('%H:%M:%S')}")

def main():
    print("RAT Monitor Started - Monitoring for suspicious activity...")
    print(f"Alerts will be saved to: {os.path.abspath(LOG_FILE)}")
    print("Press Ctrl+C to stop\n")
    
    while True:
        check_suspicious_connections()
        check_after_hours()
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()