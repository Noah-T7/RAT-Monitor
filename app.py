from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import datetime
import os
import os
print("Templates folder:", os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__)
app.secret_key = "sacco_monitor_2026"

# Simple user database
USERS = {
    "admin": "admin123",
    "auditor": "audit123"
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
    for line in result.stdout.splitlines():
        if "ESTABLISHED" in line:
            for port in suspicious_ports:
                if f":{port}" in line:
                    connections.append({"line": line.strip(), "suspicious": True})
                    break
            else:
                connections.append({"line": line.strip(), "suspicious": False})
    return connections[:20]

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error), 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    alerts = get_alerts()
    now = datetime.datetime.now()
    after_hours = now.hour >= 20 or now.hour < 6
    return render_template("dashboard.html", 
        alerts=alerts, 
        user=session["user"],
        time=now.strftime("%Y-%m-%d %H:%M:%S"),
        after_hours=after_hours,
        alert_count=len(alerts))

@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect(url_for("login"))
    connections = get_connections()
    return render_template("logs.html", connections=connections, user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)