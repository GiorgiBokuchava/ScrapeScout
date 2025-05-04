import application.jobs_ge as jobs_ge
import application.search_options as search_options
from application import db
from application.models import Job
from sqlalchemy.exc import OperationalError
from flask import current_app


def scrape_all_jobs():
    # Scrape all jobs from all sites and save them to the database

    SITES = {
        "jobs_ge": (search_options.search_config["jobs_ge"], jobs_ge.scrape_jobs_ge),
        # "another_site":
    }

    for site, (config, scrape) in SITES.items():
        for location in config["locations"]:
            for category in config["categories"]:
                if location == "" or category == "":
                    print(
                        f"Skipping location: {location} and category: {category} as they will scrape all at once."
                    )
                    continue

                print(
                    f"Scraping jobs from jobs.ge for location: {location} and category: {category}"
                )
                # Scrape jobs from jobs_ge
                site_list = scrape(location, category, "")
                print(
                    f"Scraped {len(site_list)} jobs from jobs.ge for location: {location} and category: {category}"
                )

                # Save the scraped jobs to the database
                new_jobs = 0
                for job in site_list:
                    # add location as part of dedupe key
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

                current_app.logger.info(
                    "Added %d new out of %d scraped (%s / %s)",
                    new_jobs,
                    len(site_list),
                    location,
                    category,
                )
                # TODO Update category and location in the database

            # Commit changes after processing all categories for current location
            try:
                db.session.commit()
                current_app.logger.info(f"Committed changes for location: {location}")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(
                    f"Error committing changes for location {location}: {str(e)}"
                )
                raise


# TODO New plan: scrape the entire main page using selenium to get basic info and save it to the database. If the user clicks on a job or adds to favorite, scrape the details using requests.
def get_jobs(searched_location, searched_category, searched_keyword):
    query = db.session.query(Job).filter(
        Job.location == searched_location, Job.category == searched_category
    )

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
