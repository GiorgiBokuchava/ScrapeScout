import application.jobs_ge as jobs_ge
import application.search_options as search_options


# TODO New plan: scrape the entire main page using selenium to get basic info and save it to the database. If the user clicks on a job or adds to favorite, scrape the details using requests.
def get_jobs(searched_location, searched_category, searched_keyword):
    jobs_ge_list = jobs_ge.scrape_jobs_ge(
        searched_location, searched_category, searched_keyword
    )
    # jobs_another_site_list = another_site.scrape_jobs_another_site(searched_location, searched_category, keyword)
    # Combine the results from different sites
    all_jobs_list = []
    for job in jobs_ge_list:
        if not any(
            existing_job.title == job.title and existing_job.company == job.company
            for existing_job in all_jobs_list
        ):
            print("..." + str(job))
            all_jobs_list.append(job)

    # repeat for other sites
    return all_jobs_list
