"""
MTN Mobile Money Agent - 3D Portfolio Website
-----------------------------------------------
A Flask-powered portfolio site for an MTN Mobile Money / Airtime / Bundle
agent in Ghana. Features a Three.js 3D animated hero section, a quick-order
form (Airtime, Data Bundle, Send/Receive Money) backed by SQLite, a contact
form, and a simple password-protected admin dashboard to review orders and
messages.

Run:
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000 in your browser.

Personalize the site by editing the SITE_CONFIG dictionary below, and by
replacing static/images/profile.jpg with her real photo.
"""

import os
import re
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g, jsonify
)

# --------------------------------------------------------------------------
# App setup
# --------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mtn-agent-dev-secret-change-me")

# Simple admin password (change via environment variable in production)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "momo2024")

# --------------------------------------------------------------------------
# PERSONALIZATION — edit this to customize the whole site in one place
# --------------------------------------------------------------------------
SITE_CONFIG = {
    "name": "Rydia",
    "brand": "Rydia MoMo & Airtime",
    "tagline": "Your Trusted MTN Mobile Money Agent in Ghana",
    "subtitle": "Fast Airtime \u2022 Data Bundles \u2022 Send & Receive Money",
    "bio": (
        "I'm Rydia, a certified MTN Mobile Money Agent based in Manso Akwasiso, "
        "Ghana. For over 4 years I've helped thousands of customers buy "
        "airtime, grab the best data bundle deals, and send or receive money "
        "safely and instantly. Reliable service, fair rates, and a smile "
        "every time you visit my shop."
    ),
    "location": "Manso Akwasiso \u2014 Ghana",
    "phone_display": "054 851 2306",
    "phone_tel": "+233548512306",
    "whatsapp_number": "233548512306",  # digits only, no + , used for wa.me link
    "email": "rydia.momo.agent@example.com",
    "momo_number": "054 851 2306",
    "agent_id": "MTN-MOMO-AGT-00921",
    "years_active": 4,
    "customers_served": 5200,
    "transactions_monthly": 3100,
    "rating": 4.9,
    "social": {
        "facebook": "#",
        "instagram": "#",
        "twitter": "#",
        "tiktok": "#",
    },
    "hours": [
        ("Monday - Friday", "7:00 AM - 9:00 PM"),
        ("Saturday", "8:00 AM - 9:00 PM"),
        ("Sunday", "10:00 AM - 7:00 PM"),
    ],
}

SERVICES = [
    {
        "key": "airtime",
        "icon": "📱",
        "title": "Airtime Top-Up",
        "desc": "Instant MTN airtime recharge for yourself or a loved one, "
                "any amount, any time.",
        "points": ["Instant delivery", "All networks welcome", "No extra charges"],
    },
    {
        "key": "bundle",
        "icon": "🌐",
        "title": "Data Bundles",
        "desc": "Best-value MTN data bundles — daily, weekly or monthly — "
                "delivered straight to your line.",
        "points": ["Social, SME & iShare bundles", "Student discounts", "24/7 availability"],
    },
    {
        "key": "send_money",
        "icon": "💸",
        "title": "Send Money",
        "desc": "Send Mobile Money to any network across Ghana quickly and "
                "securely from my shop.",
        "points": ["Any network", "Low fees", "Instant transfer"],
    },
    {
        "key": "receive_money",
        "icon": "💰",
        "title": "Cash-In / Cash-Out",
        "desc": "Deposit cash into your MoMo wallet or withdraw cash from "
                "your wallet safely.",
        "points": ["Secure transactions", "Printed receipt on request", "Friendly service"],
    },
    {
        "key": "bills",
        "icon": "🧾",
        "title": "Bill Payments",
        "desc": "Pay ECG, Ghana Water, DSTV/GOtv and school fees via Mobile "
                "Money right here.",
        "points": ["ECG & Water bills", "TV subscriptions", "School fees"],
    },
    {
        "key": "registration",
        "icon": "🪪",
        "title": "SIM & MoMo Registration",
        "desc": "New SIM registration and Mobile Money wallet opening with "
                "full Ghana Card verification.",
        "points": ["New SIM cards", "MoMo wallet setup", "Ghana Card verification"],
    },
]

TESTIMONIALS = [
    {
        "name": "Kwame Owusu",
        "role": "Regular Customer",
        "text": "Rydia is the fastest and most reliable agent in Manso Akwasiso. "
                "I never worry about failed transactions with her.",
    },
    {
        "name": "Efua Asante",
        "role": "Shop Owner",
        "text": "I send money for my business supplies through her every "
                "week. Always professional and quick.",
    },
    {
        "name": "Yaw Boateng",
        "role": "Student",
        "text": "Best data bundle prices around campus. She even opens early "
                "for us before class!",
    },
]

NETWORKS = ["MTN", "Vodafone/Telecel", "AirtelTigo"]

PHONE_RE = re.compile(r"^(?:\+233|0)\d{9}$")


# --------------------------------------------------------------------------
# Database helpers
# --------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            network TEXT,
            amount TEXT,
            recipient TEXT,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


# --------------------------------------------------------------------------
# Auth decorator for admin routes
# --------------------------------------------------------------------------
def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in to access the admin dashboard.", "error")
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


# --------------------------------------------------------------------------
# Context processor — makes SITE_CONFIG & services available in all templates
# --------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {
        "site": SITE_CONFIG,
        "services": SERVICES,
        "current_year": datetime.now().year,
    }


# --------------------------------------------------------------------------
# Public routes
# --------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template(
        "index.html",
        testimonials=TESTIMONIALS,
        networks=NETWORKS,
    )


@app.route("/order", methods=["POST"])
def place_order():
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    network = request.form.get("network", "").strip()
    amount = request.form.get("amount", "").strip()
    recipient = request.form.get("recipient", "").strip()
    notes = request.form.get("notes", "").strip()

    errors = []
    if not full_name:
        errors.append("Please enter your full name.")
    if not PHONE_RE.match(phone):
        errors.append("Please enter a valid Ghana phone number (e.g. 024XXXXXXX).")
    valid_services = {s["key"] for s in SERVICES}
    if service not in valid_services:
        errors.append("Please choose a valid service.")

    if errors:
        for err in errors:
            flash(err, "error")
        return redirect(url_for("home") + "#order")

    db = get_db()
    db.execute(
        """
        INSERT INTO orders
            (full_name, phone, service, network, amount, recipient, notes, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
        """,
        (
            full_name, phone, service, network, amount, recipient, notes,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ),
    )
    db.commit()

    flash(
        f"Thank you {full_name.split(' ')[0]}! Your request has been received. "
        f"{SITE_CONFIG['name']} will contact you shortly on {phone}.",
        "success",
    )
    return redirect(url_for("home") + "#order")


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()

    errors = []
    if not name:
        errors.append("Please enter your name.")
    if not message:
        errors.append("Please enter a message.")

    if errors:
        for err in errors:
            flash(err, "error")
        return redirect(url_for("home") + "#contact")

    db = get_db()
    db.execute(
        "INSERT INTO messages (name, email, phone, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, message, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    db.commit()

    flash("Message sent! Thank you for reaching out — I'll reply soon.", "success")
    return redirect(url_for("home") + "#contact")


# --------------------------------------------------------------------------
# Admin routes
# --------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Welcome back!", "success")
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        flash("Incorrect password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    orders = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    messages = db.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()

    stats = {
        "total_orders": len(orders),
        "pending_orders": sum(1 for o in orders if o["status"] == "Pending"),
        "completed_orders": sum(1 for o in orders if o["status"] == "Completed"),
        "total_messages": len(messages),
    }
    return render_template(
        "admin_dashboard.html", orders=orders, messages=messages, stats=stats
    )


@app.route("/admin/order/<int:order_id>/toggle", methods=["POST"])
@admin_required
def toggle_order(order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order:
        new_status = "Completed" if order["status"] == "Pending" else "Pending"
        db.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
        db.commit()
        flash(f"Order #{order_id} marked as {new_status}.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/order/<int:order_id>/delete", methods=["POST"])
@admin_required
def delete_order(order_id):
    db = get_db()
    db.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    db.commit()
    flash(f"Order #{order_id} deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/message/<int:message_id>/delete", methods=["POST"])
@admin_required
def delete_message(message_id):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    db.commit()
    flash(f"Message #{message_id} deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/api/stats")
@admin_required
def api_stats():
    db = get_db()
    orders = db.execute("SELECT service, status FROM orders").fetchall()
    service_counts = {}
    for o in orders:
        service_counts[o["service"]] = service_counts.get(o["service"], 0) + 1
    return jsonify(service_counts)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

