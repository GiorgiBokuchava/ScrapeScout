from bs4 import BeautifulSoup
import requests
import re
from application import db
from application.models import Job
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime, timedelta
from pytz import utc
from application.location import loc_to_site_code, site_code_to_loc, LOC_BY_KEY
from application.category import cat_to_site_code, site_code_to_cat, CAT_BY_KEY

# Georgian month names mapping
GEORGIAN_MONTHS = {
    "იანვარი": 1,
    "თებერვალი": 2,
    "მარტი": 3,
    "აპრილი": 4,
    "მაისი": 5,
    "ივნისი": 6,
    "ივლისი": 7,
    "აგვისტო": 8,
    "სექტემბერი": 9,
    "ოქტომბერი": 10,
    "ნოემბერი": 11,
    "დეკემბერი": 12,
}

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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        job_page = requests.get(job_URL, timeout=10, headers=headers)
        job_page.raise_for_status()
        job_soup = BeautifulSoup(job_page.text, "html.parser")

        # First check for English version link
        english_link = job_soup.find("a", text="ინგლისურ ენაზე")
        if english_link and english_link.get("href"):
            # Construct full URL for English version
            english_url = "https://www.jobs.ge" + english_link["href"]
            try:
                english_page = requests.get(english_url, timeout=10, headers=headers)
                english_page.raise_for_status()
                english_soup = BeautifulSoup(english_page.text, "html.parser")
                description = english_soup.find(
                    "td", attrs={"style": "padding-top:30px; padding-bottom:40px;"}
                )
                if description:
                    # Process description to preserve links
                    for link in description.find_all("a"):
                        # For mailto links, keep the email address but remove the mailto: part and query parameters
                        if link.get("href", "").startswith("mailto:"):
                            email = link.get("href")[7:]  # Remove 'mailto:' prefix
                            email = email.split("?")[0]  # Remove any query parameters
                            link.replace_with(email)
                        else:
                            # Replace other links with text and URL in a readable format
                            link.replace_with(f"{link.text} {link.get('href', '')}")
                    return description
            except Exception as e:
                pass

        # Fall back to original description if English version not available or failed
        description = job_soup.find(
            "td", attrs={"style": "padding-top:30px; padding-bottom:40px;"}
        )
        if description:
            # Process description to preserve links
            for link in description.find_all("a"):
                # For mailto links, keep the email address but remove the mailto: part and query parameters
                if link.get("href", "").startswith("mailto:"):
                    email = link.get("href")[7:]  # Remove 'mailto:' prefix
                    email = email.split("?")[0]  # Remove any query parameters
                    link.replace_with(email)
                else:
                    # Replace other links with text and URL in a readable format
                    link.replace_with(f"{link.text} {link.get('href', '')}")
            return description
        else:
            return "N/A"
    except requests.exceptions.Timeout:
        return "N/A"
    except requests.exceptions.RequestException as e:
        return "N/A"
    except Exception as e:
        return "N/A"


def extractEmail(description):
    email = ""
    found = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", description)
    if found:
        email = found.group(0).strip()
    return email if email else "N/A"


def parse_jobs_ge_date(date_str: str) -> datetime:
    """Parse a jobs.ge date string into a timezone-aware datetime object."""
    if not date_str or date_str == "N/A":
        return datetime.now(utc)

    # Handle "today" and "yesterday"
    if date_str == "დღეს":
        return datetime.now(utc)
    if date_str == "გუშინ":
        return datetime.now(utc) - timedelta(days=1)

    # Parse regular date format (e.g., "30 აპრილი")
    try:
        day, month = date_str.split()
        day = int(day)
        month = GEORGIAN_MONTHS[month]
        year = datetime.now(utc).year
        return datetime(year, month, day, tzinfo=utc)
    except (ValueError, KeyError):
        return datetime.now(utc)


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
