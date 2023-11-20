import requests
from bs4 import BeautifulSoup

url = "https://selenium-python.readthedocs.io"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

links = []
for link in soup.find_all("a"):
    href = link.get("href")

    # if href and href.startswith(url):
    links.append(href)

print(links)

# for link in links:
#     response = requests.get(link)
#     soup = BeautifulSoup(response.content, "html.parser")
    # file_name = link.replace("/", "_")
    # with open(file_name + ".txt", "w", encoding="utf-8") as f:
    #     f.write(soup.get_text())

requests.session().close()
