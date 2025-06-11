from flask import current_app
from sqlalchemy.exc import OperationalError

from application import db
from application.models import Job

from application.jobs_ge import scrape_jobs_ge
from application.location import LOCATIONS, LOC_BY_KEY
from application.category import CATEGORIES, CAT_BY_KEY

from application import jobs_ge


def _scrape_locations() -> dict[str, Job]:
    results, total = {}, 0
    for loc in LOCATIONS:
        if loc.key in ("", "ALL"):  # skip "All Locations"
            continue
        current_app.logger.info("Scraping by location: %s", loc.display)
        site_list = scrape_jobs_ge(loc.key, "ALL", "")
        total += len(site_list)
        results.update({j.url: j for j in site_list})
    current_app.logger.info("Scraped %d jobs across all locations", total)
    return results


def _scrape_categories() -> dict[str, Job]:
    results, total = {}, 0
    for cat in CATEGORIES:
        if cat.key in ("", "ALL"):
            continue
        current_app.logger.info("Scraping by category: %s", cat.display)
        site_list = scrape_jobs_ge("ALL", cat.key, "")
        total += len(site_list)
        results.update({j.url: j for j in site_list})
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
        # Preserve the location key and display from the location job
        job.location = location_jobs[url].location
        job.location_key = location_jobs[url].location_key
        to_add.append(job)

    # Category-only jobs -> keep category, set location to ""
    for url in category_only_urls - existing_urls:
        job = category_jobs[url]
        job.location_key = "ALL"  # Explicitly set to ALL for category-only jobs
        to_add.append(job)

    # Location-only jobs -> keep location, set category to ""
    for url in location_only_urls - existing_urls:
        job = location_jobs[url]
        job.category_key = "ALL"  # Explicitly set to ALL for location-only jobs
        to_add.append(job)

    # Bulk-insert—one round-trip, same as before
    if to_add:
        db.session.bulk_save_objects(to_add)
        db.session.commit()
        current_app.logger.info("Committed %d new jobs", len(to_add))
    else:
        current_app.logger.info("No new jobs to commit")


def get_jobs(
    searched_location: str,
    searched_category: str,
    searched_keyword: str,
    sort_by: str = "date_posted_desc",
):
    """Filter jobs in the DB by location, category and/or free-text keyword."""
    query = db.session.query(Job)

    if searched_location != "ALL":
        # Filter by location key and handle legacy data
        query = query.filter(
            (Job.location_key == searched_location)
            | (Job.location == LOC_BY_KEY[searched_location].display)
        )

    if searched_category != "ALL":
        # Filter by category key and handle legacy data
        query = query.filter(
            (Job.category_key == searched_category)
            | (Job.category == CAT_BY_KEY[searched_category].display)
        )

    if searched_keyword:
        kw = f"%{searched_keyword}%"
        query = query.filter(Job.title.ilike(kw) | Job.description.ilike(kw))

    # Apply sorting
    if sort_by:
        field, direction = sort_by.rsplit("_", 1)
        if field == "date_posted":
            # For date sorting, we need to handle the DD-MM-YYYY format
            from sqlalchemy import func, cast, Integer
            
            # Split the date string and cast components to integers
            day = cast(func.split_part(Job.date_posted, '-', 1), Integer)
            month = cast(func.split_part(Job.date_posted, '-', 2), Integer)
            year = cast(func.split_part(Job.date_posted, '-', 3), Integer)
            
            # Order by year, then month, then day
            if direction == "desc":
                query = query.order_by(year.desc(), month.desc(), day.desc())
            else:
                query = query.order_by(year.asc(), month.asc(), day.asc())
        else:
            # For other fields, use direct sorting
            order = db.desc(field) if direction == "desc" else db.asc(field)
            query = query.order_by(order)

    try:
        return query.all()
    except OperationalError as e:
        txt = str(e).lower()
        if "no such column" in txt or "does not exist" in txt:
            db.session.rollback()
            current_app.logger.warning("Column mismatch in DB; returning no results.")
            return []
        raise
