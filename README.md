# 🚗 ParkEasy - Parking Slot Booking System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1.3-purple.svg)](https://getbootstrap.com/)

> A modern, cinema-style parking slot booking system built with Flask and inspired by BookMyShow's elegant UI design.

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

ParkEasy is a sophisticated parking slot booking system that provides an intuitive, cinema-style interface for reserving parking spaces. The system features three distinct parking categories with dynamic pricing, real-time availability updates, and a premium user experience designed to rival modern booking platforms.

### Key Highlights

- 🎨 **BookMyShow-inspired UI** - Dark theme with gradient effects and smooth animations
- 🏷️ **Three-tier pricing system** - VIP (₹500), Executive (₹350), and Normal (₹320) categories
- 💰 **Dynamic fee structure** - Static platform fee (₹18) and night surcharge (₹12)
- 📱 **Responsive design** - Optimized for desktop, tablet, and mobile devices
- ⚡ **Real-time updates** - Instant booking confirmations and availability status
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
