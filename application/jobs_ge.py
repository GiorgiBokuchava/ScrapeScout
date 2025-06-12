from bs4 import BeautifulSoup
import requests
import re
from application import db
from application.models import Job
from datetime import datetime, timedelta
from pytz import utc
from application.location import loc_to_site_code, site_code_to_loc, LOC_BY_KEY
from application.category import cat_to_site_code, site_code_to_cat, CAT_BY_KEY
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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

# Common headers for all requests
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

def get_fully_loaded_html(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return ""


def extractDescription(job_URL):
    logger.info(f"Attempting to fetch description for URL: {job_URL}")
    try:
        job_page = requests.get(job_URL, timeout=10, headers=HEADERS)
        logger.info(f"Initial request status code: {job_page.status_code}")
        job_page.raise_for_status()
        job_soup = BeautifulSoup(job_page.text, "html.parser")
        logger.info("Successfully parsed initial page")

        # First check for English version link
        english_link = job_soup.find("a", text="ინგლისურ ენაზე")
        if english_link and english_link.get("href"):
            logger.info("Found English version link")
            # Construct full URL for English version
            english_url = "https://www.jobs.ge" + english_link["href"]
            logger.info(f"Attempting to fetch English version: {english_url}")
            try:
                english_page = requests.get(english_url, timeout=10, headers=HEADERS)
                logger.info(f"English version request status code: {english_page.status_code}")
                english_page.raise_for_status()
                english_soup = BeautifulSoup(english_page.text, "html.parser")
                description = english_soup.find(
                    "td", attrs={"style": "padding-top:30px; padding-bottom:40px;"}
                )
                if description:
                    logger.info("Found description in English version")
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
                    logger.warning("No description found in English version")
            except Exception as e:
                logger.error(f"Error fetching English version: {str(e)}")
                logger.error(f"Response content: {english_page.text if 'english_page' in locals() else 'No response'}")
                pass

        # Fall back to original description if English version not available or failed
        logger.info("Attempting to find description in original page")
        description = job_soup.find(
            "td", attrs={"style": "padding-top:30px; padding-bottom:40px;"}
        )
        if description:
            logger.info("Found description in original page")
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
            logger.warning(f"No description found for URL: {job_URL}")
            logger.debug(f"Page content: {job_page.text[:1000]}...")  # Log first 1000 chars of page content
            return "N/A"
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching job description: {job_URL}")
        return "N/A"
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching job description: {job_URL} - {str(e)}")
        logger.error(f"Response content: {job_page.text if 'job_page' in locals() else 'No response'}")
        return "N/A"
    except Exception as e:
        logger.error(f"Unexpected error fetching job description: {job_URL} - {str(e)}")
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

    # Parse regular date format (e.g., "30 აპრილი")
    try:
        day, month = date_str.split()
        day = int(day)
        month = GEORGIAN_MONTHS[month]
        current_date = datetime.now(utc)
        year = current_date.year

        # If the month is greater than current month, use previous year
        if month > current_date.month:
            year -= 1

        return datetime(day=day, month=month, year=year, tzinfo=utc)
    except (ValueError, KeyError):
        return datetime.now(utc)


def get_paginated_html(base_url: str) -> str:
    """
    Gets HTML from all pages by checking for duplicates.
    Starts from page 2 since page 1 is already fetched by get_fully_loaded_html.
    Returns combined HTML from all unique pages.
    """
    combined_html = ""
    page_num = 2
    last_html = ""
    
    while True:
        paginated_url = f"{base_url}&page={page_num}&for_scroll=yes"
        logger.info(f"Fetching page {page_num}...")
        
        try:
            response = requests.get(paginated_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            current_html = response.text
            
            # If we get the same HTML as last time, we've reached the end
            if current_html == last_html:
                logger.info(f"Reached end at page {page_num-1}")
                break
                
            combined_html += current_html
            last_html = current_html
            page_num += 1
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {page_num}: {e}")
            break
    
    return combined_html


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
        logger.warning(f"Invalid location key {chosen_job_location}")
        site_location_id = ""
    if chosen_job_category != "ALL" and site_category_id is None:
        logger.warning(f"Invalid category key {chosen_job_category}")
        site_category_id = ""

    # Build base URL with validated IDs
    base_url = f"https://jobs.ge/?q={chosen_job_keyword}"
    if site_category_id not in (None, ""):
        base_url += f"&cid={site_category_id}"
    if site_location_id not in (None, ""):
        base_url += f"&lid={site_location_id}&jid=0&in_title=0&has_salary=0&is_ge=0"

    logger.info(f"Starting scrape with URL: {base_url}")

    # Get first page HTML
    first_page_html = get_fully_loaded_html(base_url)
    if not first_page_html:
        logger.error("Failed to fetch first page")
        return []

    # Get remaining pages HTML
    remaining_pages_html = get_paginated_html(base_url)
    
    # Combine all HTML
    full_html = first_page_html + remaining_pages_html
    
    soup = BeautifulSoup(full_html, "html.parser")

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
            formatted_date = parsed_date.strftime("%d-%m-%Y")

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
            
            # Log each job's details
            logger.info(f"""
Found Job:
---------------
Title: {new_job.title}
Company: {new_job.company}
URL: {new_job.url}
Date Posted: {new_job.date_posted}
Location: {new_job.location}
Location Key: {new_job.location_key}
Category: {new_job.category}
Category Key: {new_job.category_key}
---------------
""")
            
        except Exception as e:
            logger.error(f"Error processing job row: {e}")
            continue

    logger.info(f"Scraping complete. Found {len(jobs)} jobs for location: {chosen_job_location}, category: {chosen_job_category}")
    return jobs
