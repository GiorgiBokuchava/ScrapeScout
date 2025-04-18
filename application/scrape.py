import application.jobs_ge as jobs_ge


def get_jobs(searched_location, searched_category, searched_keyword):
    jobs_ge_list = jobs_ge.scrape_jobs_ge(
        searched_location, searched_category, searched_keyword
    )
    # jobs_another_site_list = another_site.scrape_jobs_another_site(searched_location, searched_category, keyword)
    # Combine the results from different sites
    all_jobs_list = []
    for job in jobs_ge_list:
        if not any(
            existing_job.title == job.title
            and existing_job.company_name == job.company_name
            for existing_job in all_jobs_list
        ):
            all_jobs_list.append(job)

    # repeat for other sites
    return all_jobs_list
