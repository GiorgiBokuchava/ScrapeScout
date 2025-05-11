# ScrapeScout

ScrapeScout is a **Flask‑based job aggregation platform** that collects vacancies from multiple Georgian job boards (starting with *jobs.ge*) and presents them through a single, modern interface. It scrapes data, stores it in a database, and lets users search, preview and bookmark listings – all inside a Dockerised stack that runs the same locally and in the cloud.

---

## Key Features

* **Multi‑site scraping** with Selenium + BeautifulSoup (dynamic pages fully rendered).
* **Scheduled indexing** every six hours via APScheduler.
* **PostgreSQL / SQLite storage** accessed through SQLAlchemy models.
* **Full‑text search & rich filters** (region, city, category, keyword, sort).
* **User accounts** powered by Flask‑Login and bcrypt password hashing.
* **Bookmark system** – save jobs to a favourites list.
* **Responsive UI** with dark‑mode toggle, real‑time preview panel and email copy helper.
* **Containerised deployment** – one `docker compose up` launches web + db.
* **Render.com ready** – configuration file provided for one‑click cloud deploy.

---

## Technology Stack

* **Backend:** Python 3.11, Flask, SQLAlchemy, APScheduler
* **Scraping:** Selenium (headless Chrome), BeautifulSoup 4
* **Frontend:** HTML 5, Jinja2 templates, vanilla JavaScript, Font Awesome, CSS variables
* **Database:** PostgreSQL in production, SQLite for local quick‑start
* **Auth & Security:** Flask‑Login, bcrypt, CSRF protection via Flask‑WTF
* **Containerisation:** Docker, Docker Compose, Gunicorn

---

## Quick Start (Docker)

```bash
git clone https://github.com/GiorgiBokuchava/ScrapeScout.git
cd ScrapeScout
cp .env.example .env            # edit values if desired
docker compose up --build       # launches web (port 5000) and db (port 5432)
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### Required Environment Variables

* `SECRET_KEY` – any random string for Flask sessions.
* `DATABASE_URL` – connection string for Postgres (`postgresql://user:pass@db:5432/scrapescout`).
* `SELENIUM_DRIVER` – path or command for headless Chrome (defaults work in the container).

The provided **`.env.example`** lists sensible defaults for local development.

---

## Running Without Docker

```bash
python -m venv env && source env/bin/activate
pip install -r requirements.txt
export SECRET_KEY="dev-secret"
export DATABASE_URL="sqlite:///instance/scrape.db"
flask db upgrade
python run.py
```

The app starts on [http://localhost:5000](http://localhost:5000). Selenium requires a local Chrome/Chromium + chromedriver in `$PATH`.

---

## Project Layout (abridged)

```
ScrapeScout/
│  run.py                    # entrypoint
│  docker-compose.yaml       # dev stack (web + db)
│  Dockerfile                # builds the web image
│  render.yaml               # Render.com service definition
├─ application/
│   ├─ models.py             # User, Job ORM models
│   ├─ jobs_ge.py            # scraper for jobs.ge
│   ├─ scrape.py             # indexing & query helpers
│   ├─ routes.py             # Flask controllers
│   ├─ forms.py              # WTForms classes
│   └─ scheduler.py          # APScheduler setup
├─ templates/                # Jinja2 HTML files
├─ static/                   # JS, CSS, SVG assets
├─ migrations/               # Alembic versions
└─ README.md
```

---

## Contributing

1. Fork the repo and create a new branch (e.g. `feature/new-board`).
2. Commit your changes with clear messages.
3. Push and open a Pull Request describing the enhancement.

Please run `black` for formatting and ensure `pytest` passes before submitting.

---

## License

This project is released under the **MIT License**. See `LICENSE` for full text.

---

## Contact

* GitHub: [https://github.com/GiorgiBokuchava](https://github.com/GiorgiBokuchava)
* Email: listed in GitHub profile

Happy scraping! 🚀
