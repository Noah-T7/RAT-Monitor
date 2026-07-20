from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import subprocess
import datetime
import os
import json

app = Flask(__name__)
app.secret_key = "sacco_monitor_2026"

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "auditor": {"password": "audit123", "role": "auditor"},
    "staff": {"password": "staff123", "role": "staff"},
    "noah": {"password": "noah123", "role": "staff"}
}

def get_alerts():
    alerts = []
    log_file = "rat_alerts.txt"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f.readlines():
                if "[ALERT]" in line:
                    alerts.append(line.strip())
    return alerts

def get_connections():
    result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
    connections = []
    suspicious_ports = [4444, 1234, 5555, 8080]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for line in result.stdout.splitlines():
        if "ESTABLISHED" in line:
            for port in suspicious_ports:
                if f":{port}" in line:
                    connections.append({
                        "line": line.strip(),
                        "suspicious": True,
                        "time": timestamp
                    })
                    break
            else:
                connections.append({
                    "line": line.strip(),
                    "suspicious": False,
                    "time": timestamp
                })
    return connections[:20]

def log_session(username, action):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("session_logs.txt", "a") as f:
        f.write(f"[{action.upper()}] {timestamp} - User: {username}\n")

def ask_ai(question, alerts, sessions):
    total_alerts = len(alerts)
    port_4444 = sum(1 for a in alerts if "4444" in a)
    port_1234 = sum(1 for a in alerts if "1234" in a)
    after_hours_count = sum(1 for a in alerts if "After-hours" in a)
    suspicious_ports = sum(1 for a in alerts if "Suspicious connection" in a)
    login_events = [s for s in sessions if "LOGIN" in s]
    logout_events = [s for s in sessions if "LOGOUT" in s]
    total_sessions = len(sessions)

    if port_4444 > 0 or port_1234 > 0:
        threat_level = "CRITICAL"
        threat_color = "RED ALERT"
    elif suspicious_ports > 0:
        threat_level = "HIGH"
        threat_color = "HIGH RISK"
    elif after_hours_count > 5:
        threat_level = "MEDIUM"
        threat_color = "CAUTION"
    elif total_alerts > 0:
        threat_level = "LOW"
        threat_color = "LOW RISK"
    else:
        threat_level = "SAFE"
        threat_color = "ALL CLEAR"

    q = question.lower()

    if "hi" in q or "hello" in q or "hey" in q:
        return ("Hello! I am your SACCO Security AI Assistant.\n\n"
                "I can help you with:\n"
                "- Analyzing security alerts\n"
                "- Checking for suspicious connections\n"
                "- Reviewing staff login activity\n"
                "- Recommending actions to take\n"
                "- Blocking attackers\n\n"
                "Current system status: " + threat_color + " - " + threat_level + "\n"
                "Total alerts recorded: " + str(total_alerts) + "\n\n"
                "How can I help you today?")

    elif "thank" in q or "thanks" in q or "okay" in q:
        return ("You are welcome! Stay vigilant and keep monitoring your system.\n\n"
                "Remember:\n"
                "- Check alerts daily\n"
                "- Keep rat_monitor.py running\n"
                "- Report any suspicious activity immediately\n\n"
                "Is there anything else I can help you with?")

    elif "help" in q or "what can you do" in q or "capabilities" in q:
        return ("I am your SACCO Security AI Assistant. Here is what I can do:\n\n"
                "Security Analysis:\n"
                "- Analyze current security alerts\n"
                "- Detect suspicious network connections\n"
                "- Identify after-hours activity\n"
                "- Assess threat levels\n\n"
                "Staff Monitoring:\n"
                "- Review staff login and logout times\n"
                "- Flag after-hours staff access\n"
                "- Track session history\n\n"
                "Incident Response:\n"
                "- Recommend immediate actions\n"
                "- Provide firewall blocking commands\n"
                "- Guide evidence preservation\n\n"
                "Try asking me:\n"
                "- What happened at 2AM?\n"
                "- How serious are the alerts?\n"
                "- How do I block the attacker?")

    elif "2am" in q or "after hours" in q or "night" in q:
        if after_hours_count > 0:
            return ("AFTER-HOURS ACTIVITY DETECTED\n\n"
                    "The system recorded " + str(after_hours_count) + " after-hours alerts.\n\n"
                    "What this means:\n"
                    "- Someone is active on this computer outside working hours\n"
                    "- This is a strong indicator of RAT activity\n"
                    "- The attacker may be conducting unauthorized transactions\n\n"
                    "Recommended actions:\n"
                    "1. Check if any staff member was legitimately working\n"
                    "2. Review session logs for active accounts\n"
                    "3. Contact your bank to freeze any pending transactions\n"
                    "4. Do not turn off the computer - preserve evidence")
        else:
            return "No after-hours activity detected. System is operating normally within business hours."

    elif "suspicious" in q or "connection" in q or "port" in q:
        if suspicious_ports > 0:
            return ("SUSPICIOUS CONNECTIONS DETECTED - Threat Level: " + threat_level + "\n\n"
                    "Detected " + str(suspicious_ports) + " suspicious connections:\n"
                    "- Port 4444 connections: " + str(port_4444) + " (Metasploit RAT indicator)\n"
                    "- Port 1234 connections: " + str(port_1234) + " (RAT backdoor indicator)\n\n"
                    "These ports are NOT used by legitimate software.\n\n"
                    "Immediate actions:\n"
                    "1. Disconnect from internet immediately\n"
                    "2. Screenshot everything first\n"
                    "3. Call your cybersecurity team\n"
                    "4. Contact the bank to freeze the account\n"
                    "5. Preserve rat_alerts.txt as forensic evidence")
        else:
            return "No suspicious connections detected on known RAT ports. Network activity appears normal."

    elif "serious" in q or "risk" in q or "dangerous" in q:
        return ("Current Threat Assessment: " + threat_level + "\n\n"
                "Alert Summary:\n"
                "- Total alerts: " + str(total_alerts) + "\n"
                "- After-hours alerts: " + str(after_hours_count) + "\n"
                "- Suspicious connections: " + str(suspicious_ports) + "\n"
                "- Port 4444 (RAT indicator): " + str(port_4444) + "\n\n"
                "Staff Activity:\n"
                "- Login events: " + str(len(login_events)) + "\n"
                "- Logout events: " + str(len(logout_events)))

    elif "staff" in q or "login" in q or "logged in" in q:
        if sessions:
            recent = sessions[-5:] if len(sessions) >= 5 else sessions
            session_list = "\n".join(recent)
            warning = "WARNING: After-hours logins detected!" if after_hours_count > 0 else "All sessions appear normal."
            return ("Staff Login Activity Analysis\n\n"
                    "Total events: " + str(total_sessions) + "\n"
                    "Logins: " + str(len(login_events)) + "\n"
                    "Logouts: " + str(len(logout_events)) + "\n\n"
                    "Recent activity:\n" + session_list + "\n\n" + warning)
        else:
            return "No staff session data recorded yet."

    elif "block" in q or "stop" in q or "disconnect" in q:
        if suspicious_ports > 0 or port_4444 > 0:
            return ("ACTIVE THREAT - Blocking Recommended\n\n"
                    "Run this in Command Prompt as Administrator:\n\n"
                    "netsh advfirewall firewall add rule name=BlockRAT dir=out action=block remoteport=4444,1234,5555,8080 protocol=tcp\n\n"
                    "This will block all outbound connections on RAT ports.\n\n"
                    "After blocking:\n"
                    "1. Contact your bank immediately\n"
                    "2. Change all passwords from a different device\n"
                    "3. Report to cybersecurity authorities")
        else:
            return "No active threats detected that require blocking at this time."

    elif "do" in q or "action" in q or "recommend" in q or "should" in q:
        if threat_level in ["CRITICAL", "HIGH"]:
            return ("IMMEDIATE ACTION REQUIRED - Threat Level: " + threat_level + "\n\n"
                    "Step 1 - RIGHT NOW:\n"
                    "- Take screenshots of all alert screens\n"
                    "- Note the exact time and date\n\n"
                    "Step 2 - Within 5 minutes:\n"
                    "- Disconnect from internet\n"
                    "- Call your bank and freeze the account\n"
                    "- Do NOT turn off the computer\n\n"
                    "Step 3 - Within 1 hour:\n"
                    "- Contact cybersecurity professionals\n"
                    "- Preserve rat_alerts.txt as evidence\n"
                    "- File a report with authorities")
        else:
            return ("System Status: " + threat_level + " - Operating normally.\n\n"
                    "Routine recommendations:\n"
                    "1. Keep rat_monitor.py running at all times\n"
                    "2. Check dashboard daily for new alerts\n"
                    "3. Ensure Sysmon is running in Event Viewer\n"
                    "4. Review staff login times weekly\n"
                    "5. Run a full system scan monthly")

    else:
        return ("System Status: " + threat_color + " - Threat Level: " + threat_level + "\n\n"
                "Security Alerts: " + str(total_alerts) + " total\n"
                "- After-hours activity: " + str(after_hours_count) + " incidents\n"
                "- Suspicious connections: " + str(suspicious_ports) + " detected\n"
                "- Port 4444 (RAT indicator): " + str(port_4444) + "\n\n"
                "Staff Activity: " + str(total_sessions) + " session events\n\n"
                "Ask me anything! For example:\n"
                "- Hi / Hello\n"
                "- What happened at 2AM?\n"
                "- How serious are the alerts?\n"
                "- What should I do right now?\n"
                "- Was any staff logged in after hours?\n"
                "- How do I block the attacker?")


@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    role = session.get("role")
    if role == "admin" or role == "auditor":
        return redirect(url_for("dashboard"))
    return redirect(url_for("staff_dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            session["role"] = USERS[username]["role"]
            log_session(username, "login")
            if USERS[username]["role"] in ["admin", "auditor"]:
                return redirect(url_for("dashboard"))
            return redirect(url_for("staff_dashboard"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    if session.get("role") not in ["admin", "auditor"]:
        return redirect(url_for("staff_dashboard"))
    alerts = get_alerts()
    now = datetime.datetime.now()
    after_hours = now.hour >= 20 or now.hour < 6
    sessions = []
    if os.path.exists("session_logs.txt"):
        with open("session_logs.txt", "r") as f:
            for line in f.readlines():
                sessions.append(line.strip())
    return render_template("dashboard.html",
        alerts=alerts,
        user=session["user"],
        role=session["role"],
        time=now.strftime("%Y-%m-%d %H:%M:%S"),
        after_hours=after_hours,
        alert_count=len(alerts),
        sessions=sessions[-10:])


@app.route("/staff")
def staff_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    now = datetime.datetime.now()
    after_hours = now.hour >= 20 or now.hour < 6
    sessions = []
    if os.path.exists("session_logs.txt"):
        with open("session_logs.txt", "r") as f:
            for line in f.readlines():
                if session["user"] in line:
                    sessions.append(line.strip())
    return render_template("staff_dashboard.html",
        user=session["user"],
        time=now.strftime("%Y-%m-%d %H:%M:%S"),
        after_hours=after_hours,
        sessions=sessions[-10:])


@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect(url_for("login"))
    if session.get("role") not in ["admin", "auditor"]:
        return redirect(url_for("staff_dashboard"))
    connections = get_connections()
    return render_template("logs.html", connections=connections, user=session["user"])


@app.route("/ai-chat", methods=["POST"])
def ai_chat():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    question = request.json.get("question", "")
    alerts = get_alerts()
    sessions_data = []
    if os.path.exists("session_logs.txt"):
        with open("session_logs.txt", "r") as f:
            sessions_data = [line.strip() for line in f.readlines()]
    response = ask_ai(question, alerts, sessions_data)
    return jsonify({"response": response})


@app.route("/logout")
def logout():
    if "user" in session:
        log_session(session["user"], "logout")
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)