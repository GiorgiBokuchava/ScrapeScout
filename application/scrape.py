from flask import current_app
from sqlalchemy.exc import OperationalError
from application import db
from application.models import Job
from application.jobs_ge import scrape_jobs_ge
from application.search_options import MASTER_CONFIG, search_config


def index_all_jobs():
    """
    Scrape all jobs from all sites and save them to the database.
    Commits changes after processing each category for a location.
    """
    # Index all jobs from jobs.ge
    for location in search_config["jobs_ge"]["locations"]:
        for category in search_config["jobs_ge"]["categories"]:
            if location == "" or category == "":
                print(
                    f"Skipping location: {location} and category: {category} as they will scrape all at once."
                )
                continue

            print(
                f"Scraping jobs from jobs.ge for location: {location} and category: {category}"
            )

            try:
                # Scrape jobs from jobs_ge
                site_list = scrape_jobs_ge(location, category, "")
                print(
                    f"Scraped {len(site_list)} jobs from jobs.ge for location: {location} and category: {category}"
                )

                # Save the scraped jobs to the database
                new_jobs = 0
                for job in site_list:
                    # Check if job already exists
                    exists = (
                        db.session.query(Job)
                        .filter_by(
                            title=job.title,
                            url=job.url,
                        )
                        .first()
                    )
                    if exists:
                        current_app.logger.debug(
                            "Skip existing job: %s - %s @%s",
                            job.title,
                            job.company,
                            job.location,
                        )
                    else:
                        db.session.add(job)
                        new_jobs += 1

                # Commit changes after processing each category
                try:
                    db.session.commit()
                    current_app.logger.info(
                        "Added %d new out of %d scraped (%s / %s)",
                        new_jobs,
                        len(site_list),
                        location,
                        category,
                    )
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(
                        f"Error committing changes for location {location}, category {category}: {str(e)}"
                    )

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(
                    f"Error processing location {location}, category {category}: {str(e)}"
                )
                # Continue to next category instead of raising the exception
                continue

    # Index all jobs from another site
    # (Add code here when needed)


def get_jobs(searched_location, searched_category, searched_keyword):
    """
    Get jobs from the database based on search criteria.
    """
    # index_all_jobs()  # Commented out to prevent reindexing on every search
    query = db.session.query(Job)

    if searched_location != "ALL":
        # Use the display value from master config for filtering
        location_display = MASTER_CONFIG["locations"].get(searched_location)
        if location_display:
            query = query.filter(Job.location == location_display)

    if searched_category != "ALL":
        # Use the display value from master config for filtering
        category_display = MASTER_CONFIG["categories"].get(searched_category)
        if category_display:
            query = query.filter(Job.category == category_display)

    if searched_keyword:
        kw = f"%{searched_keyword}%"
        query = query.filter(Job.title.ilike(kw) | Job.description.ilike(kw))

    try:
        return query.all()
    except OperationalError as e:
        txt = str(e).lower()
        if "no such column" in txt or "does not exist" in txt:
            db.session.rollback()
            current_app.logger.warning(
                "Category filter failed or column missing; returning no results."
            )
            return []
        raise
