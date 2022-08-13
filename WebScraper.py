import requests
from bs4 import BeautifulSoup
import pandas as pd

"""
Utilise Beautiful Soup library to scrape all NAMI CHAPTER contact information from NAMI Website including
[phone number,
email,
website,
counties chapter serves]
"""


def getPhoneNumber():
    """Method to scrape phone number from contact information table on NAMI County page"""
    phone_number = city_soup.find_all("tr",
                                      id="p_lt_WebPartZone8_ZoneMainContent_pageplaceholder_p_lt_ctl01_AffiliateLanding_Details_ctl00_rowPhone")
    try:
        citi_NAMI_data.append(phone_number[0].text.strip()[8:])
    except IndexError:
        citi_NAMI_data.append("N/A")
        # print("Phone Number Not Found")


def getEmail():
    """Method to scrape email from contact information table on NAMI County page"""
    # id="p_lt_WebPartZone8_ZoneMainContent_pageplaceholder_p_lt_ctl01_AffiliateLanding_Details_ctl00_rowEmail"
    email = city_soup.find_all("tr",
                               id="p_lt_WebPartZone8_ZoneMainContent_pageplaceholder_p_lt_ctl01_AffiliateLanding_Details_ctl00_rowEmail")
    try:
        citi_NAMI_data.append((cfDecodeEmail(email[0].find('a')['href'][28:])))
        # print((cfDecodeEmail(email[0].find('a')['href'][28:])))
    except IndexError:
        citi_NAMI_data.append("N/A")
        # print("Email Not Found")


def cfDecodeEmail(encodedString):
    """
    Method to decode cloudflare protected email addresses

    Paramters
    ---------
    :param encodedString: str
    """

    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i + 2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


def getWebsite():
    """
    Method to scrape website url from contact information table on NAMI County page
    """
    website = city_soup.find_all("tr",
                                 id="p_lt_WebPartZone8_ZoneMainContent_pageplaceholder_p_lt_ctl01_AffiliateLanding_Details_ctl00_rowWebsite")
    try:
        citi_NAMI_data.append((website[0].find('a')['href']))
        # print((website[0].find('a')['href']))
    except IndexError:
        citi_NAMI_data.append("N/A")
        # print("Email Not Found")


def getServing():
    """
    Method to scrape the counties served from contact information table on NAMI County page
    """
    serving = city_soup.find_all("tr",
                                 id="p_lt_WebPartZone8_ZoneMainContent_pageplaceholder_p_lt_ctl01_AffiliateLanding_Details_ctl00_rowServing")
    try:
        citi_NAMI_data.append(serving[0].text[10:].strip())
        # print(serving[0].text[10:].strip())
    except IndexError:
        # print("Serving Not Found")
        citi_NAMI_data.append("N/A")


states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
data = []
citi_NAMI_data = []

for state in states:
    URL = f"https://nami.org/Find-Your-Local-NAMI/Affiliate?state={state}"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    nami_content = soup.find(class_="nami-content")
    citi_NAMI_details = nami_content.find_all("td", class_="name")
    for city in citi_NAMI_details:
        # https://nami.org/Find-Your-Local-NAMI/Affiliate/Program-Details-(1)?state=CT&local=0011Q000022GBnZQAW
        city_code = city.find('a')['href'][-27:-25]
        # print(city_code)
        local_code = city.find('a')['href'][-18:]
        # print(local_code)
        city_url = f"https://nami.org/Find-Your-Local-NAMI/Affiliate/Program-Details-(1)?state={state}&local={local_code}"
        city_page = requests.get(city_url)
        city_soup = BeautifulSoup(city_page.content, "html.parser")
        # print(city_soup.prettify())
        city_content = city_soup.find(class_="panel panel-primary")

        citi_NAMI_data.append(state)
        getWebsite()
        getEmail()
        getPhoneNumber()
        getServing()
        data.append(citi_NAMI_data.copy())
        citi_NAMI_data.clear()
        print(f"Processed {state}")
df = pd.DataFrame(data, columns=["State", "Website", "Email", "Phone Number", "Serving"])
df["Population_2021"] = None
df.to_pickle("NAMI_DATA.pkl")
# df.to_csv("./NAMI_CONTACTS.csv")
print(df.to_string())
