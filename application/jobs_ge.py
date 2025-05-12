from bs4 import BeautifulSoup
import requests
import re
from application import db
from application.models import Job
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import locale

# ← new imports
from application.location import loc_to_site_code, site_code_to_loc, LOC_BY_KEY
from application.category import cat_to_site_code, site_code_to_cat

# Set locale for Georgian month names
try:
    locale.setlocale(locale.LC_TIME, "ka_GE.UTF-8")
except locale.Error:
    # Fallback to English if Georgian locale is not available
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")

job_keyword = ""  # &q=KEYWORD


def build_driver() -> webdriver.Chrome:
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_opts)


def get_fully_loaded_html(url: str) -> str:
    driver = build_driver()
    driver.get(url)
    time.sleep(1)

    last_h = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h

    html = driver.page_source
    driver.quit()
    return html


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
        email = found.group(0).strip()
    return email if email else "N/A"


def parse_jobs_ge_date(date_str: str) -> datetime:
    """Parse jobs.ge date format into datetime object."""
    try:
        # Remove any extra whitespace
        date_str = date_str.strip()

        # Get current year
        current_year = datetime.now().year

        # Try to parse the date
        try:
            # First try with Georgian month names
            date_obj = datetime.strptime(f"{date_str} {current_year}", "%d %B %Y")
        except ValueError:
            # If that fails, try with English month names
            date_obj = datetime.strptime(f"{date_str} {current_year}", "%d %B %Y")

        # If the parsed date is in the future, it's probably from last year
        if date_obj > datetime.now():
            date_obj = date_obj.replace(year=current_year - 1)

        return date_obj
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return datetime.now()


def scrape_jobs_ge(
    chosen_job_location: str, chosen_job_category: str, chosen_job_keyword: str
) -> list[Job]:
    """
    chosen_job_location / chosen_job_category are canonical keys:
      e.g. "TBILISI", "SALES", or "ALL"
    """
    site = "jobs_ge"
    # Get both ids properly or defaults
    site_location_id = (
        ""
        if chosen_job_location == "ALL"
        else loc_to_site_code(site, chosen_job_location)
    )
    site_category_id = (
        ""
        if chosen_job_category == "ALL"
        else cat_to_site_code(site, chosen_job_category)
    )

    # Verify we got valid IDs if not "ALL"
    if chosen_job_location != "ALL" and site_location_id is None:
        print(f"Warning: Invalid location key {chosen_job_location}")
        site_location_id = ""
    if chosen_job_category != "ALL" and site_category_id is None:
        print(f"Warning: Invalid category key {chosen_job_category}")
        site_category_id = ""

    # Build URL with validated IDs
    url = f"https://jobs.ge/?page=1&q={chosen_job_keyword}"
    if site_category_id not in (None, ""):
        url += f"&cid={site_category_id}"
    if site_location_id not in (None, ""):
        url += f"&lid={site_location_id}&jid="

    print(f"Scraping URL: {url}")  # Debug log

    html = get_fully_loaded_html(url)
    soup = BeautifulSoup(html, "html.parser")

    jobs: list[Job] = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        try:
            title = tds[1].find("a").text.strip()
            company = tds[3].text.strip()
            # skip ads / pagination rows
            if any(w in company for w in ["ყველა", "ვაკანსია"]):
                continue

            href = tds[1].find("a")["href"]
            job_url = "https://www.jobs.ge" + href

            posted = tds[4].text.strip()
            if any(w in posted for w in ["ყველა", "ვაკანსია"]):
                continue

            # Parse the date
            parsed_date = parse_jobs_ge_date(posted)
            formatted_date = parsed_date.strftime("%Y-%m-%d")

            # Look up display names and ensure we have valid objects
            loc_obj = None
            cat_obj = None

            if site_location_id:
                loc_obj = site_code_to_loc(site, site_location_id)
            if site_category_id:
                cat_obj = site_code_to_cat(site, site_category_id)

            # Create job with proper location/category info and default description/email
            new_job = Job(
                title=title,
                company=company,
                url=job_url,
                date_posted=formatted_date,
                salary="N/A",
                email="...",
                location_key=chosen_job_location,
                category_key=chosen_job_category,
                location=(
                    loc_obj.display
                    if loc_obj
                    else (
                        LOC_BY_KEY[chosen_job_location].display
                        if chosen_job_location != "ALL"
                        else "All Locations"
                    )
                ),
                category=cat_obj.display if cat_obj else "All Categories",
                description="...",
            )
            jobs.append(new_job)
        except Exception as e:
            print("scrape error:", e)
            continue

    print(
        f"Found {len(jobs)} jobs for location: {chosen_job_location}, category: {chosen_job_category}"
    )
    return jobs
