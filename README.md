# ScrapeScout

ScrapeScout is a Flask‑based job aggregation platform that collects vacancies from Georgian job boards (currently *jobs.ge*) and delivers a single, modern search experience. It scrapes data, stores it in a database, and lets users search, preview and bookmark listings – all inside a Dockerised stack that runs the same in development and production.

---

## Key Features

• Multi‑site scraping with Selenium + BeautifulSoup (dynamic pages rendered in headless Chrome).

• Six‑hourly scheduled indexing via APScheduler.

• PostgreSQL (Render.com) or SQLite (local) storage accessed through SQLAlchemy models.

• Full‑text search and rich filters for region, city, category, keyword and sort order.

• User accounts protected by Flask‑Login and bcrypt.

• One‑click bookmarks (favourites) with instant email copy.

• Responsive UI with dark‑mode toggle and real‑time preview panel.

• Containerised deployment – one `docker compose up` boots web + db.

• Render.com configuration supplied for hassle‑free cloud deploy.

---

## Technology Stack

Backend: Python 3.11, Flask, SQLAlchemy, APScheduler
Scraping: Selenium, BeautifulSoup 4
Frontend: HTML 5, Jinja2, vanilla JavaScript, CSS variables, Font Awesome
Database: PostgreSQL (prod) or SQLite (dev)
Auth & Security: Flask‑Login, bcrypt, CSRF protection via Flask‑WTF
Containerisation: Docker, Docker Compose, Gunicorn

---

## Quick Start with Docker

```bash
git clone https://github.com/GiorgiBokuchava/ScrapeScout.git
cd ScrapeScout
cp .env.example .env        # adjust values if you like
docker compose up --build   # launches web on :8000 and db on :5432
```

Browse to [http://localhost:8000](http://localhost:8000).

### Required Environment Variables

• `FLASK_APP` – entrypoint module (defaults to `run.py`).
• `FLASK_DEBUG` – `1` for hot‑reload in development.
• `DATABASE_URL` – Postgres or SQLite URI.
• `SCRAPE_SCOUT_SECRET_KEY` – secret key for session & CSRF.
• `PORT` – web server port (inside container).

An **`.env.example`** template is provided – copy it and fill any secrets.

---

## Running Without Docker

```bash
python -m venv env
source env/bin/activate (or env\Scripts\activate if ur on Windows)
pip install -r requirements.txt
export FLASK_APP=run.py
export FLASK_DEBUG=1
export SCRAPE_SCOUT_SECRET_KEY="devsecret123"
export DATABASE_URL="sqlite:///instance/scrape.db" // for local db
export PORT=8000
flask db upgrade
python run.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser. Selenium requires a local Chrome/Chromium and chromedriver in `$PATH`.

---

## .env.example

```
# Flask settings
FLASK_APP=run.py
FLASK_DEBUG=1
PORT=8000

# Database (choose one)
# For local dev – uncomment below line to store data in an on‑disk SQLite file
# DATABASE_URL=sqlite:///instance/scrape.db

# For Docker Compose local Postgres
# DATABASE_URL=postgresql://scrape:secret@db:5432/scrapedb

# For Render.com cloud Postgres (uncomment when deploying)
# DATABASE_URL=postgresql://scrape_scout_db_user:REPLACE_ME@dpg‑xxxx.frankfurt‑postgres.render.com/scrape_scout_db?sslmode=require

# Secret key used for sessions and CSRF; change in production!
SCRAPE_SCOUT_SECRET_KEY=devsecret123
```

---

## Project Layout (overview)

```
ScrapeScout/
  run.py                # entrypoint
  docker-compose.yaml   # dev stack (web + db)
  Dockerfile            # builds web image
  render.yaml           # Render.com service definition
  .env.example          # sample configuration
  application/
    models.py           # User, Job ORM models
    jobs_ge.py          # scraper for jobs.ge
    scrape.py           # indexing & query helpers
    routes.py           # Flask controllers
    forms.py            # WTForms classes
    scheduler.py        # APScheduler setup
  templates/            # Jinja2 HTML files
  static/               # JS, CSS, SVG assets
  migrations/           # Alembic versions
```

---

## Contributing

1. Fork the repository and create a feature branch.
2. Commit changes using conventional commit messages.
3. Run `black` for formatting and ensure tests pass.
4. Open a Pull Request describing the enhancement.

---

## License

Released under the **MIT License**. See `LICENSE` for full text.

---

## Contact

GitHub: [https://github.com/GiorgiBokuchava](https://github.com/GiorgiBokuchava)

Happy scraping! 🚀
