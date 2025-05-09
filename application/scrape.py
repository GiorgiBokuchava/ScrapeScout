from flask import current_app
from sqlalchemy.exc import OperationalError

from application import db
from application.models import Job
from application.jobs_ge import scrape_jobs_ge
from application.search_options import MASTER_CONFIG, search_config


def _scrape_locations() -> dict[str, Job]:
    # Scrape every configured location once and return {url: Job}.
    results: dict[str, Job] = {}
    total = 0

    for loc_key, loc_val in search_config["jobs_ge"]["locations"].items():
        if not loc_key:  # empty key means “ALL”; we skip it
            continue

        current_app.logger.info("Scraping jobs.ge for location: %s", loc_val)
        site_list = scrape_jobs_ge(loc_key, "", "")  # (location, category, kw)
        total += len(site_list)
        for job in site_list:
            results[job.url] = job

        current_app.logger.info(
            "Scraped %d jobs for location: %s", len(site_list), loc_val
        )

    current_app.logger.info("Scraped %d jobs across all locations", total)
    return results


def _scrape_categories() -> dict[str, Job]:
    # Scrape every configured category once and return {url: Job}.
    results: dict[str, Job] = {}
    total = 0

    for cat_key, cat_val in search_config["jobs_ge"]["categories"].items():
        if not cat_key:
            continue

        current_app.logger.info("Scraping jobs.ge for category: %s", cat_val)
        site_list = scrape_jobs_ge("", cat_key, "")
        total += len(site_list)
        for job in site_list:
            results[job.url] = job

        current_app.logger.info(
            "Scraped %d jobs for category: %s", len(site_list), cat_val
        )

    current_app.logger.info("Scraped %d jobs across all categories", total)
    return results


def index_all_jobs() -> None:
    # Scrape, validate and bulk-insert jobs from jobs.ge.
    location_jobs = _scrape_locations()  # {url: Job}
    category_jobs = _scrape_categories()  # {url: Job}

    # Compute the three disjoint URL sets
    common_urls = set(location_jobs) & set(category_jobs)
    category_only_urls = set(category_jobs) - common_urls
    location_only_urls = set(location_jobs) - common_urls

    all_urls = common_urls | category_only_urls | location_only_urls
    if not all_urls:
        current_app.logger.warning("No jobs scraped at all")
        return

    # One query: which of those URLs are already in the DB?
    existing_urls = {
        u for (u,) in db.session.query(Job.url).filter(Job.url.in_(all_urls)).all()
    }

    # Build new Job objects entirely in memory
    to_add: list[Job] = []

    # Jobs found in both passes -> merge location + category
    for url in common_urls - existing_urls:
        job = category_jobs[url]
        job.location = location_jobs[url].location
        to_add.append(job)

    # Category-only jobs -> keep category, set location to ""
    for url in category_only_urls - existing_urls:
        job = category_jobs[url]
        to_add.append(job)

    # Location-only jobs -> keep location, set category to ""
    for url in location_only_urls - existing_urls:
        job = location_jobs[url]
        to_add.append(job)

    # Bulk-insert—one round-trip, same as before
    if to_add:
        db.session.bulk_save_objects(to_add)
        db.session.commit()
        current_app.logger.info("Committed %d new jobs", len(to_add))
    else:
        current_app.logger.info("No new jobs to commit")


def get_jobs(searched_location: str, searched_category: str, searched_keyword: str):
    # Filter jobs in the DB by location, category and/or free-text keyword.

    query = db.session.query(Job)

    if searched_location != "ALL":
        loc_display = MASTER_CONFIG["locations"].get(searched_location)
        if loc_display:
            query = query.filter(Job.location == loc_display)

    if searched_category != "ALL":
        cat_display = MASTER_CONFIG["categories"].get(searched_category)
        if cat_display:
            query = query.filter(Job.category == cat_display)

    if searched_keyword:
        kw = f"%{searched_keyword}%"
        query = query.filter(Job.title.ilike(kw) | Job.description.ilike(kw))

    try:
        return query.all()
    except OperationalError as e:
        txt = str(e).lower()
        if "no such column" in txt or "does not exist" in txt:
            db.session.rollback()
            current_app.logger.warning("Column mismatch in DB; returning no results.")
            return []
        raise
