from bs4 import BeautifulSoup
import requests
import re
from application import db
from application.models import Job
from application.search_options import get_master_to_site_mapping, MASTER_CONFIG
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


job_keyword = ""  # &q=KEYWORD


def extractDescription(job_URL):
    job_page = requests.get(job_URL)
    job_soup = BeautifulSoup(job_page.text, "html.parser")
    description = job_soup.find(
        "td", attrs={"style": "padding-top:30px; padding-bottom:40px;"}
    )
    return description if description else "N/A"


def extractEmail(description):
    email = ""
    found = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", description)
    if found:
        email = found.group(0)
    return email if email else "N/A"


def build_driver() -> webdriver.Chrome:
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=chrome_opts)


# Get html content of the page using Selenium (because of infinite loading)
def get_fully_loaded_html(url):
    driver = build_driver()
    driver.get(url)

    TIME_TO_WAIT = 2  # seconds

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(TIME_TO_WAIT)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html_content = driver.page_source
    driver.quit()
    return html_content


def scrape_jobs_ge(chosen_job_location, chosen_job_category, chosen_job_keyword):
    """
    This function scrapes jobs.ge for the given location, category, and keyword.
    It returns a list of Job objects.
    """
    # Get mappings from master config to jobs.ge specific values
    location_mapping = get_master_to_site_mapping("jobs_ge", "locations")
    category_mapping = get_master_to_site_mapping("jobs_ge", "categories")

    # Convert master config values to site-specific values
    site_location = location_mapping.get(
        MASTER_CONFIG["locations"].get(chosen_job_location, ""), ""
    )
    site_category = category_mapping.get(
        MASTER_CONFIG["categories"].get(chosen_job_category, ""), ""
    )

    # Build the URL using site-specific values
    page_URL = f"https://www.jobs.ge/?page=1&q={chosen_job_keyword}&cid={site_category}&lid={site_location}&jid="

    ###############################
    # Scrape the website

    ##### TO RUN ON SERVER
    html_content = get_fully_loaded_html(page_URL)
    soup = BeautifulSoup(html_content, "html.parser")

    jobs_ge_list = []

    # Jobs
    tr_elements = soup.find_all("tr")

    for tr in tr_elements:
        tds = tr.find_all("td")

        if len(tds) >= 4:
            try:
                job_title = tds[1].find("a").text.strip()
                # Use the master config value for location and category
                location = MASTER_CONFIG["locations"].get(chosen_job_location, "")
                category = MASTER_CONFIG["categories"].get(chosen_job_category, "")

                company_name = tds[3].text.strip()
                skip_words = ["ყველა", "ვაკანსია", "ერთ", "გვერდზე"]
                if any(word in company_name for word in skip_words):
                    continue

                job_URL = ("https://www.jobs.ge" + tds[1].find("a")["href"]).strip()

                job_description_text = "..."

                posted_time = tds[4].text.strip()
                skip_words = ["ყველა", "ვაკანსია", "ერთ", "გვერდზე"]
                if any(word in posted_time for word in skip_words):
                    continue

                salary = "N/A"

                email = ""

                favorite = False

                new_job = Job(
                    title=job_title,
                    location=location,
                    category=category,
                    company=company_name,
                    description=job_description_text,
                    url=job_URL,
                    date_posted=posted_time,
                    salary=salary,
                    email=email,
                    favorite=favorite,
                )

                jobs_ge_list.append(new_job)
                print(f"Job added: {job_title} - {company_name}")

            except Exception as e:
                print(f"Error: {e}")
                continue

    return jobs_ge_list


"""
# Example usage
location_choice = "Tbilisi"     # or user input
category_choice = "Sales"       # or user input
keyword_choice = ""             # or user input

results = scrape_jobs(location_choice, category_choice, keyword_choice)
print(f"Found {len(results)} job(s).")
"""
