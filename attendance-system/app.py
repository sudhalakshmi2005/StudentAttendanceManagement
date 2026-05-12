from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime, date
import pandas as pd

app = Flask(__name__)
app.secret_key = "attendance_secure_2026"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

# ---------------- GET IP ----------------
def get_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For')
    return request.remote_addr

# ---------------- CHECK WIFI IP ----------------
def is_valid_ip(ip):

    # College WiFi + localhost
    return ip.startswith("10.0") or ip == "127.0.0.1"

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        user = request.form["username"]
        pwd = request.form["password"]
        mac = request.form["mac"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM students WHERE username=? AND password=?",
            (user, pwd)
        )

        data = cur.fetchone()

        conn.close()

        if data:

            session["user"] = user
            session["mac"] = mac

            return redirect("/dashboard")

        else:
            error = "Invalid Login ❌"

    return render_template("login.html", error=error)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")

    msg = ""

    ip = get_ip()
    mac = session.get("mac", "")

    device_status = ""
    ip_status = ""

    if request.method == "POST":

        conn = get_db()
        cur = conn.cursor()

        # Get original MAC
        cur.execute(
            "SELECT mac FROM students WHERE username=?",
            (session["user"],)
        )

        result = cur.fetchone()

        if result:

            db_mac = result[0]

            # ---------------- MAC CHECK ----------------
            if mac == db_mac:
                device_status = "✅ Device Verified"
            else:
                device_status = "❌ Wrong Device"

            # ---------------- IP CHECK ----------------
            if is_valid_ip(ip):
                ip_status = "✅ Inside Campus WiFi"
            else:
                ip_status = "❌ Outside Network"

            # ---------------- DUPLICATE CHECK ----------------
            today = str(date.today())

            cur.execute(
                """
                SELECT * FROM attendance
                WHERE username=?
                AND date(date_time)=?
                """,
                (session["user"], today)
            )

            already = cur.fetchone()

            if already:

                msg = "⚠ Attendance Already Marked Today"

            else:

                # ---------------- FINAL CHECK ----------------
                if is_valid_ip(ip) and mac == db_mac:

                    cur.execute(
                        """
                        INSERT INTO attendance
                        (username, mac, status, date_time)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            session["user"],
                            mac,
                            "Present",
                            datetime.now()
                        )
                    )

                    conn.commit()

                    msg = "✅ Attendance Marked Successfully"

                else:

                    cur.execute(
                        """
                        INSERT INTO attendance
                        (username, mac, status, date_time)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            session["user"],
                            mac,
                            "Rejected",
                            datetime.now()
                        )
                    )

                    conn.commit()

                    msg = "❌ Fraud Detected"

        else:

            msg = "User Not Found ❌"

        conn.close()

    return render_template(
        "dashboard.html",
        msg=msg,
        user=session["user"],
        ip=ip,
        mac=mac,
        device_status=device_status,
        ip_status=ip_status
    )

# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, mac, status, date_time
        FROM attendance
        ORDER BY date_time DESC
    """)

    data = cur.fetchall()

    conn.close()

    return render_template("admin.html", data=data)

# ---------------- EXPORT EXCEL ----------------
@app.route("/download")
def download_excel():

    conn = get_db()

    # Get all students
    students = pd.read_sql_query(
        "SELECT username FROM students",
        conn
    )

    # Get today's attendance
    today = str(date.today())

    attendance = pd.read_sql_query(
        f"""
        SELECT username, status
        FROM attendance
        WHERE date(date_time) = '{today}'
        """,
        conn
    )

    report = []

    for student in students["username"]:

        found = attendance[
            attendance["username"] == student
        ]

        if len(found) > 0:

            status = found.iloc[0]["status"]

        else:

            status = "Absent"

        report.append({
            "Username": student,
            "Date": today,
            "Status": status
        })

    df = pd.DataFrame(report)

    file_name = "attendance_report.xlsx"

    df.to_excel(file_name, index=False)

    conn.close()

    return send_file(
        file_name,
        as_attachment=True
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)