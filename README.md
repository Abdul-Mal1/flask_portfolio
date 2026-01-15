# Flask Portfolio Website (Job-Ready)

A modern portfolio website built with **Python (Flask)**.
Includes:
- Responsive sections (About / Projects / Resume / Contact)
- **Contact form saved to SQLite** database
- Optional admin JSON endpoint to view messages
- Ready to deploy on **Render**

---

## 1) Run locally

### Install
```bash
python -m venv .venv
# mac/linux
source .venv/bin/activate
# windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

### Start the server
```bash
python app.py
```

Open:
- http://127.0.0.1:5000

---

## 2) Add your resume
Place your resume PDF here:

`static/assets/Resume.pdf`

Then the "Download Resume" button will work.

---

## 3) Where are contact messages stored?
Messages are stored in:

`app.db`

Optional: view messages (admin endpoint):
- `GET /admin/messages`

### Protect the admin endpoint (recommended)
Set env var:
- `ADMIN_TOKEN=your-secret-token`

Then open:
- `/admin/messages?token=your-secret-token`

Or send header:
- `X-Admin-Token: your-secret-token`

---

## 4) Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Flask portfolio"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB/portfolio.git
git push -u origin main
```

---

## 5) Deploy to Render

**Build command**
```bash
pip install -r requirements.txt
```

**Start command**
```bash
gunicorn app:app
```

**Environment variables**
- `FLASK_SECRET_KEY` = long random string
- Optional:
  - `ADMIN_TOKEN` = long random token
  - `DB_PATH` = `/var/data/app.db` (if you add a persistent disk)

**Persistent DB (optional)**
- Add a Disk mounted at `/var/data`
- Set `DB_PATH=/var/data/app.db`

---

## 6) Customize
Edit:
- `templates/index.html` (your name, projects, links)
- `templates/layout.html` (site title, logo)
- `static/css/style.css` (colors)

---

## Tech Stack
- Python
- Flask
- SQLite
- HTML/CSS
- Minimal JS (menu only)

## License
MIT
