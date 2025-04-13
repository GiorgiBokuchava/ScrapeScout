import requests

url = "https://www.jobs.ge/"
response = requests.get(url)

# Save the HTML content to a file
with open("main_page.html", "w", encoding="utf-8") as file:
    file.write(response.text)
