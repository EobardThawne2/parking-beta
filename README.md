# 🚗 ParkEasy — Cinema-Style Parking Slot Booking System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-blue)](https://parking-beta-ten.vercel.app)

Modern parking reservation app with BookMyShow-style UI. Supports user login, admin panel, and real-time slot booking.

**TL;DR** — Get running in 2 minutes:

```powershell
git clone <repo-url>
cd "Parking V2"
pip install -r requirements.txt
python app.py
# Open http://127.0.0.1:5000
```

## What

- **User booking**: Cinema-style seat selection, VIP/Executive/Normal pricing
- **Admin panel**: Reset bookings, view statistics
- **Auth system**: User registration, login, admin-only routes
- **SQLite**: Persistent local database (with in-memory fallback for serverless)
- **Responsive UI**: Bootstrap 5 + custom CSS animations

## Quick Start

### 1. Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run

```powershell
python app.py
# Starts on http://127.0.0.1:5000
```

### 3. Default Login (Admin)
- Email: `admin@parkeasy.com`
- Password: `admin123`

## Key Features

| Feature | Details |
|---------|---------|
| **Pricing** | VIP ₹500, Executive ₹350, Normal ₹320 + ₹18 platform fee + ₹12 night surcharge (midnight–5 AM) |
| **Slots** | 10 VIP, 100 Executive, 11 Normal (121 total) |
| **API** | Booking, reset, stats, auth endpoints |
| **Deployment** | Works on Vercel (SQLite with `/tmp` fallback) and local |

## Configuration

Pricing in `app.py`:

```python
PLATFORM_FEE = 18
NIGHT_SURCHARGE = 12
parking_data = {
    'vip': {'price': 500},
    'executive': {'price': 350},
    'normal': {'price': 320}
}
```

Env vars (optional):

```powershell
$env:FLASK_ENV = 'development'
$env:FLASK_DEBUG = '1'
$env:SECRET_KEY = 'your-key'
```

## API Endpoints

### Public
- `GET /` — Home page
- `POST /api/register` — User signup
- `POST /api/login` — User login
- `GET /api/parking-status` — All slots + availability

### User (login required)
- `POST /api/book-slots` — Book slots
- `GET /api/my-bookings` — User's bookings
- `POST /api/calculate-fees` — Calculate total fees

### Admin (admin login required)
- `POST /api/reset-bookings` — Clear all bookings
- `GET /api/booking-stats` — Stats by category

### Example: Book slots

```bash
curl -X POST http://127.0.0.1:5000/api/book-slots \
  -H "Content-Type: application/json" \
  -d '{"type": "vip", "slots": ["V1", "V2"]}'
```

Response:
```json
{
  "success": true,
  "pricing": {
    "base_amount": 1000,
    "platform_fee": 18,
    "night_surcharge": 0,
    "grand_total": 1018
  },
  "booked_slots": ["V1", "V2"],
  "booking_reference": "ABC123XYZ"
}
```

## Files

```
app.py                 # Flask routes, API endpoints
database.py           # SQLite queries, booking logic
auth.py               # User auth (register, login)
templates/            # HTML (Jinja2)
  index.html          # Home
  select_seats.html   # Booking UI (cinema-style)
  admin.html          # Admin panel
static/css/style.css  # Dark theme, animations
```

## Tech Stack

- **Backend**: Flask 2.x, SQLite, Python 3.8+
- **Frontend**: Bootstrap 5, HTML5, CSS3, Vanilla JS
- **Auth**: SHA256 hashing, Flask sessions
- **Deployment**: Vercel (serverless)

## Development

- PEP8 style for Python
- No automated tests (add in `tests/` if needed)
- Reset demo data: `POST /api/reset-bookings` (admin only)
- Check logs: Watch `app.py` output

## Known Issues

- **SQLite on Vercel**: Uses `/tmp/parking.db` (writable per-function) + in-memory fallback
- **Session persistence**: User sessions reset between Vercel function invocations
- For production + persistent state → Migrate to PostgreSQL/MongoDB (see `VERCEL_DEPLOYMENT.md`)

## Deploy to Vercel

```bash
git push
# Vercel auto-detects Flask, deploys to https://parking-beta-ten.vercel.app
```

## Contributing

1. Fork repo
2. Branch: `git checkout -b feat/new-feature`
3. Commit: `git commit -m "Add feature"`
4. Push & PR

Include: motivation, changes, test steps.

## License

MIT — See `LICENSE`
# 🚗 ParkEasy — Parking Slot Booking System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)

Compact, actionable README inspired by the gitdocify style: short intro, quick start, configuration, API reference, and contribution guidelines.

TL;DR — Run locally:

```powershell
git clone <repo-url>
cd "Parking-beta"
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## What is this

ParkEasy is a demo parking-slot booking app built with Flask. It exposes a simple booking UI (cinema-style seat selection), a few JSON APIs, and a small data layer used for development.

Why this README: gitdocify-style docs are short, scannable, and focused on getting you running quickly.

## Quick links

- Source: `app.py`, `database.py`, `templates/`, `static/`
- Demo (local): `http://127.0.0.1:5000`
- Config: environment variables and a small pricing table in `app.py`

## Quick start (Windows / PowerShell)

1. Clone the repo

```powershell
git clone <repo-url>
cd "Parking-beta"
```

2. Create a virtualenv (optional, recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies

```powershell
pip install -r requirements.txt
```

4. Run

```powershell
python app.py
```

Open your browser at http://127.0.0.1:5000

## Configuration

Set these environment variables for development (PowerShell):

```powershell
$env:FLASK_ENV = 'development'
$env:FLASK_DEBUG = '1'
# $env:SECRET_KEY = 'a-secure-random-string'
```

Pricing is configured in `app.py` (search for `parking_data`, `PLATFORM_FEE`, `NIGHT_SURCHARGE`).

## Minimal API reference

Endpoints that matter for local development: brief examples.

- GET / — Home page
- GET /select-seats — Booking UI
- GET /parking — Parking layout
- GET /api/parking-status — JSON status of all slots
- POST /api/book-slots — Book slots (body: { type: string, slots: [string] })
- POST /api/calculate-fees — Compute fees (body: { base_amount })
- POST /api/reset-bookings — Reset demo bookings (admin/test)

Example response for `/api/parking-status`:

```json
{
  "vip": { "price": 500, "slots": ["V1","V2"], "booked": [] },
  "executive": { "price": 350, "slots": [], "booked": [] },
  "normal": { "price": 320, "slots": [], "booked": [] }
}
```

Notes:
- The project uses JSON files / in-memory structures for demo persistence. For production, swap to a real DB.
- The fee structure includes a platform fee and night surcharge; see `app.py` for exact values.

## Project layout

Top-level files you’ll care about:

- `app.py` — Flask app and routing
- `database.py` — small persistence helpers used by the demo
- `parking_data.json`, `parking_data1.json` — demo data
- `templates/` — Jinja2 templates (UI)
- `static/` — CSS and client assets

## Development notes

- Follow PEP8 for Python changes.
- Add tests when you change logic (there are currently no automated tests in the repo).
- Use the `/api/reset-bookings` endpoint while developing to reset demo state.

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit and push
4. Open a PR with a short description

Please include: motivation, summary of changes, and any manual steps to test.

## License

MIT — see the `LICENSE` file.

---

If you want, I can also:

- add a short `CONTRIBUTING.md` with a PR checklist
- add PowerShell-friendly dev tasks in a `Makefile` or `tasks.json`

Changes made: trimmed and reorganized the original README into a short, developer-friendly, gitdoc-style README.
