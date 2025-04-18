from bs4 import BeautifulSoup
import requests
import re
from application.Job import Job

# from application import search_options

job_locations = {
    "": "Any",
    1: "Tbilisi",
    15: "Abkhazia",
    14: "Adjara",
    9: "Guria",
    8: "Imereti",
    3: "Kakheti",
    4: "Mtskhe-Mtianeti",
    12: "Ratcha-Letchkhumi, qv. Svaneti",
    13: "Samegrelo-Zemo Svaneti",
    7: "Samtskhe-Javakheti",
    5: "Kvemo-Kartli",
    6: "Shida-Kartli",
    16: "Abroad",
    17: "Remote",
}  # &lid=NUMBER

job_categories = {
    "": "Any",
    1: "Administration/Management",
    3: "Finances/Statistics",
    2: "Sales",
    4: "PR/Marketing",
    18: "General Technical Personnel",
    5: "Logistics/Transport/Distribution",
    11: "Building/Renovation",
    16: "Cleaning",
    17: "Security",
    6: "IT/Programming",
    13: "Media/Publishing",
    12: "Education",
    7: "Law",
    8: "Medicine/Pharmacy",
    14: "Beauty/Fashion",
    10: "Food",
    9: "Other",
}  # &cid=NUMBER

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
    # CHANGED: Removed 'job_URL' param from this function signature, it wasn't being used inside it.
    # Instead, 'description' is passed directly and we rely on the HTML chunk we already have.
    """
    # If your intention was to read an <a>mailto link> from the same page:
    job_page = requests.get(job_URL)
    job_soup = BeautifulSoup(job_page.text, "html.parser")
    email = job_soup.find("a", href=re.compile(r"^mailto:"))
    return email.text if email else "N/A"
    """
    found = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", description)
    if found:
        email = found.group(0)
    return email if email else "N/A"


count = 0


def scrape_jobs_ge(chosen_job_location, chosen_job_category, chosen_job_keyword):
    """
    This function scrapes jobs.ge for the given location, category, and keyword.
    It returns a list of Job objects.
    """
    # CHANGED: user_preferences dict remains local to the function.
    user_preferences = {
        "job_location": "",
        "job_category": "",
        "job_keyword": "",
    }

    # Map the chosen location string to its dictionary key
    for key, value in job_locations.items():
        if value == chosen_job_location:
            user_preferences["job_location"] = key

    # Map the chosen category string to its dictionary key
    for key, value in job_categories.items():
        if value == chosen_job_category:
            user_preferences["job_category"] = key

    # If no keyword, keep it empty
    if chosen_job_keyword == "":
        job_keyword = ""
    else:
        job_keyword = chosen_job_keyword

    user_preferences["job_keyword"] = job_keyword

    # Build the URL from user_preferences
    page_URL = f"https://www.jobs.ge/?page=1&q={user_preferences['job_keyword']}&cid={user_preferences['job_category']}&lid={user_preferences['job_location']}&jid="

    ###############################
    # Scrape the website

    ####### TO RUN LOCALLY
    # Load the saved local HTML file
    with open("application/temps/main_page.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, "html.parser")

    ####### TO RUN ON SERVER
    # page_to_scrape = requests.get(page_URL)
    # soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    titles = soup.find_all("a", attrs={"class": "vip"})
    print(titles)

    jobs_ge_list = []

    tr_elements = soup.find_all("tr")

    # def getSalary(job_URL):
    # Too much overhead, probably not worth it

    for tr in tr_elements:
        tds = tr.find_all("td")

        if len(tds) >= 4:
            try:
                job_title = tds[1].find("a").text.strip()
                company_name = tds[3].text.strip()
                job_URL = "https://www.jobs.ge" + tds[1].find("a")["href"]

                job_description_element = extractDescription(job_URL)
                job_description_text = (
                    job_description_element.text.strip()
                    if hasattr(job_description_element, "text")
                    else str(job_description_element)
                )

                posted_time = tds[4].text.strip()
                salary = "N/A"

                email = extractEmail(job_description_text)

                favorite = False

                new_job = Job(
                    title=job_title,
                    company_name=company_name,
                    job_URL=job_URL,
                    description=job_description_text,
                    posted_time=posted_time,
                    salary=salary,
                    email=email,
                    favorite=favorite,
                )

                print(str(new_job))
                jobs_ge_list.append(new_job)
                count += 1
                if count > 2:
                    break
            except Exception as e:
                # print(f"Error: {e}")
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
