import application.jobs_ge as jobs_ge


def get_jobs(searched_location, searched_category, searched_keyword):
    jobs_ge_list = jobs_ge.scrape_jobs_ge(
        searched_location, searched_category, searched_keyword
    )
    # jobs_another_site_list = another_site.scrape_jobs_another_site(searched_location, searched_category, keyword)
    # Combine the results from different sites
    all_jobs_list = []
    for job in jobs_ge_list:
        if (
            job.title not in all_jobs_list.title
            and job.company_name not in all_jobs_list.company_name
        ):
            all_jobs_list.append(job)

    # repeat for other sites
