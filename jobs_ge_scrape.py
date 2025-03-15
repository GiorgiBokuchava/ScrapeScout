from bs4 import BeautifulSoup
import requests
import re
from Job import Job

job_locations = {
    "": "Any",
    1: "Tbilisi",
    15: "Abkhazia",
    14: "Adjara",
    9: "Guria",
    8: "Imereti",
    3: "Kakheti",
    4: "Mtskheta-Mtianeti",
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
    8: "Medicin/Pharmacy",
    14: "Beauty/Fashion",
    10: "Food",
    9: "Other",
}  # &cid=NUMBER

job_keyword = ""  # &q=KEYWORD

user_preferences = {
    "job_location": "",
    "job_category": "",
    "job_keyword": job_keyword,
}

chosen_job_location = input("Choose job location: ")
chosen_job_category = input("Choose job category: ")
chosen_job_keyword = input("Filter using keywords: ")

# chosen_job_location = "Tbilisi"
# chosen_job_category = "Sales"
# chosen_job_keyword = ""

for key, value in job_locations.items():
    if value == chosen_job_location:
        user_preferences["job_location"] = key

for key, value in job_categories.items():
    if value == chosen_job_category:
        user_preferences["job_category"] = key

if chosen_job_keyword == "":
    job_keyword = ""
else:
    job_keyword = chosen_job_keyword

user_preferences["job_keyword"] = job_keyword

page_URL = f"https://www.jobs.ge/?page=1&q={user_preferences['job_keyword']}&cid={user_preferences['job_category']}&lid={user_preferences['job_location']}&jid="

###############################

# Scrape the website

######## TO RUN LOCALLY

# # Load the saved local HTML file
# with open("main_page.html", "r", encoding="utf-8") as file:
#     html_content = file.read()

# soup = BeautifulSoup(html_content, "html.parser")


page_to_scrape = requests.get(page_URL)
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

titles = soup.findAll("a", attrs={"class": "vip"})

job_list = []

tr_elements = soup.find_all("tr")


def extractDescription(job_URL):
    job_page = requests.get(job_URL)
    job_soup = BeautifulSoup(job_page.text, "html.parser")
    description = job_soup.find(
        "td", attrs={"style": "padding-top:30px; padding-bottom:40px;"}
    )
    return description if description else "N/A"


# def getSalary(job_URL):
# Too much overhead, probably not worth it


def extractEmail(description):
    email = ""
    job_page = requests.get(job_URL)
    job_soup = BeautifulSoup(job_page.text, "html.parser")
    email = job_soup.find("a", href=re.compile(r"^mailto:"))
    return email.text if email else "N/A"


for tr in tr_elements:
    tds = tr.find_all("td")

    if len(tds) >= 4:
        try:
            job_title = tds[1].find("a").text.strip()
            company_name = tds[3].text.strip()
            job_URL = "https://www.jobs.ge/" + tds[1].find("a")["href"]
            job_description = extractDescription(job_URL).text.strip()
            posted_time = tds[4].text.strip()
            salary = "N/A"
            email = extractEmail(job_description)
            favorite = False

            new_job = Job(
                job_title,
                company_name,
                job_URL,
                job_description,
                posted_time,
                salary,
                email,
                favorite,
            )

            print(str(new_job))

            job_list.append(new_job)
        except Exception as e:
            print(f"Error: {e}")
