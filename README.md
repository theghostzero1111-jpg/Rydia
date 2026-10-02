# Rydia MoMo & Airtime — 3D Portfolio Website

A **Python (Flask)** portfolio website for an MTN Mobile Money agent in Ghana.
She sells **airtime**, **data bundles**, and **sends/receives money**.

## Features

- 3D animated hero section (Three.js): spinning gold coin, orbiting mini-coins, gold particle field, mouse parallax
- Services section (Airtime, Bundles, Send Money, Cash-In/Out, Bills, SIM registration)
- About section with agent ID badge, contact info and working hours
- Quick Order form (saved to SQLite with Ghana phone validation)
- Testimonials section
- Contact form (saved to SQLite)
- Floating WhatsApp chat button
- Admin dashboard at `/admin` (default password: `momo2024`) to view/complete/delete orders and messages
- Fully responsive + MTN yellow/black theme

## Quick Start

```powershell
cd mtn-agent-portfolio
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Customize

Edit `SITE_CONFIG` in `app.py` — name, phone, WhatsApp number,
MoMo number, location, hours, bio. Default admin password can be
changed with the `ADMIN_PASSWORD` environment variable:

```powershell
$env:ADMIN_PASSWORD = "your-secret-password"
python app.py
```

## Project Structure

```
mtn-agent-portfolio/
├── app.py                  # Flask backend, routes, SQLite DB
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── admin_login.html
│   └── admin_dashboard.html
└── static/
    ├── css/style.css
    └── js/
        ├── hero3d.js        # Three.js 3D hero scene
        └── main.js          # Navbar, counters, reveal animations
```
