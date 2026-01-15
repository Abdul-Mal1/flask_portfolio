import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import smtplib
from email.message import EmailMessage
from time import time
RATE_LIMIT = {}  # ip -> [timestamps]


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-in-production")

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "app.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            ip TEXT,
            user_agent TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/resume")
def resume():
    # Put your resume PDF in: static/assets/Resume.pdf
    filename = "Resume.pdf"
    asset_dir = os.path.join(app.root_path, "static", "assets")
    path = os.path.join(asset_dir, filename)
    if not os.path.exists(path):
        flash("Resume file not found. Add static/assets/Resume.pdf", "warning")
        return redirect(url_for("home") + "#resume")
    return send_from_directory(asset_dir, filename, as_attachment=True)

@app.route("/contact", methods=["POST"])
def contact():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    subject = (request.form.get("subject") or "").strip()
    message = (request.form.get("message") or "").strip()
    # Honeypot: if filled, likely a bot
    website = (request.form.get("website") or "").strip()
    if website:
        return ("", 204)  # silently ignore
    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
    if is_rate_limited(ip):
        flash("Too many messages. Please wait and try again.", "warning")
        return redirect(url_for("home") + "#contact")
    
    if not name or not email or not message:
        flash("Please fill in name, email, and message.", "error")
        return redirect(url_for("home") + "#contact")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO messages (name, email, subject, message, created_at, ip, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            subject,
            message,
            datetime.utcnow().isoformat() + "Z",
            request.headers.get("X-Forwarded-For", request.remote_addr),
            request.headers.get("User-Agent", ""),
        ),
    )
    conn.commit()
    conn.close()
# Send email notification (optional)
    try:
        send_contact_email(name, email, subject, message)
    except Exception:
        # Do not break the site if email fails
        pass
    
    flash("Message sent! I’ll get back to you soon.", "success")
    return redirect(url_for("home") + "#contact")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/admin")
def admin_page():
    token = os.getenv("ADMIN_TOKEN")
    if token:
        provided = request.headers.get("X-Admin-Token") or request.args.get("token")
        if provided != token:
            return "Unauthorized", 401

    conn = get_db()
    rows = conn.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 200").fetchall()
    conn.close()
    return render_template("admin.html", messages=rows)

# Optional: Admin endpoint to view messages in JSON.
# Protect with ADMIN_TOKEN environment variable.
@app.route("/admin/messages")
def admin_messages():
    token = os.getenv("ADMIN_TOKEN")
    if token:
        provided = request.headers.get("X-Admin-Token") or request.args.get("token")
        if provided != token:
            return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    rows = conn.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 200").fetchall()
    conn.close()
    return jsonify({"messages": [dict(r) for r in rows]})

init_db()

def send_contact_email(name: str, email: str, subject: str, message: str):
    host = os.getenv("MAIL_HOST")
    port = int(os.getenv("MAIL_PORT", "587"))
    user = os.getenv("MAIL_USER")
    password = os.getenv("MAIL_PASS")
    to_addr = os.getenv("MAIL_TO")
    from_addr = os.getenv("MAIL_FROM", user)

    # If email isn't configured, just skip (still saves to DB)
    if not all([host, user, password, to_addr]):
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Portfolio Contact: {subject or 'New message'}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(
        f"New message from your portfolio contact form:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n"
    )

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)

    return True

def is_rate_limited(ip: str, limit: int = 5, window_seconds: int = 60) -> bool:
    now = time()
    timestamps = RATE_LIMIT.get(ip, [])
    # keep only timestamps within window
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= limit:
        RATE_LIMIT[ip] = timestamps
        return True
    timestamps.append(now)
    RATE_LIMIT[ip] = timestamps
    return False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)
