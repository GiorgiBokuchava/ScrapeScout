from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from application.scrape import scrape_all_jobs


def start_scheduler(app):
    """Fire scrape_all_jobs() once every 24 h."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: app.app_context().push() or scrape_all_jobs(),
        trigger=IntervalTrigger(
            days=1, start_date=datetime.now() + timedelta(seconds=5)
        ),
        id="daily_scrape",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    # scheduler.start() # Uncomment this line to start the scheduler
