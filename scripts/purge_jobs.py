from application import app, db
from application.models import Job

with app.app_context():
    deleted = Job.query.delete()
    db.session.commit()
    print(f"Deleted {deleted} rows")

# docker compose run --rm -w /app app python -m scripts.purge_jobs
