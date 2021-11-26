# accessing google sheet https://developers.google.com/sheets/api/quickstart/python
# $ sudo pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from __future__ import print_function
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

# $ sudo pip3 install selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    ElementNotSelectableException,
    ElementNotVisibleException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotInteractableException,
)
from selenium.webdriver.support.ui import WebDriverWait

# access local development environment variables from .env file
# $ sudo pip3 install python-decouple
from decouple import config

import time
import datetime
import csv

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(1)


# search key words
businesstype = "restaurant"


def main():

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    googleDrive = build("drive", "v3", credentials=creds)

    with open("CanadaCities.csv", mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        currentProvince = ""
        currentCity = ""
        for csvRow in csv_reader:
            if csvRow["ranking"] in ["3", "4"]:  # only scrapping tier 3 and 4 cities
                if (
                    currentProvince != csvRow["province_id"]
                ):  # create new google sheet file when we get a new province
                    # this works because the csv file has been sorted by province
                    spreadsheet = (
                        googleDrive.files()
                        .create(
                            body={
                                "name": f"{businesstype} in {csvRow['province_name']}",
                                "parents": [config("folderId")],
                                "mimeType": "application/vnd.google-apps.spreadsheet",
                                "sheets": [
                                    {
                                        "properties": {"title": csvRow["city"]},
                                    }
                                ],
                            },
                            fields="id",
                        )
                        .execute()
                    )
                    spreadsheetId = spreadsheet.get("id")
                    currentProvince = csvRow["province_id"]

                # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets
                if currentCity != csvRow["city"]:  # create new sub sheet for a new city
                    spreadsheet = (
                        service.spreadsheets()
                        .batchUpdate(
                            spreadsheetId=spreadsheetId,
                            body={
                                "requests": [
                                    {
                                        "addSheet": {
                                            "properties": {"title": csvRow["city"]}
                                        }
                                    }
                                ]
                            },
                        )
                        .execute()
                    )

                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet.get("spreadsheetId"),
                        range=f"{csvRow['city']}!A1",
                        valueInputOption="RAW",
                        body={
                            "values": [
                                [
                                    "ID",
                                    "target",
                                    "IG follow date",
                                    "IG message date time",
                                    "IG URL",
                                    "FB follow date",
                                    "FB message date time",
                                    "FB URL",
                                    "Name",
                                    "website",
                                    "Rating",
                                    "Review count",
                                    "Store type",
                                    "Phone",
                                    "Address",
                                    "City",
                                    "Province / Postal Code",
                                    "3rd party online order url",
                                    "Date crawled",
                                    "size/number of table",
                                    "msg template ID Status",
                                    "Comments",
                                ]
                            ]
                        },
                    ).execute()

                    currentCity = csvRow["city"]

                # starting point in the google sheet
                rowNum = 2
                updatedRange = f"{csvRow['city']}!I{rowNum}"

                driver.get(
                    f"https://www.google.com/search?q={csvRow['city']}+{csvRow['province_name']}+{businesstype}"
                )
                print(
                    f"https://www.google.com/search?q={csvRow['city']}+{csvRow['province_name']}+{businesstype}"
                )
                driver.find_element(
                    "xpath", "//span[contains(text(),'View all')]"
                ).click()

                nextPage = True  # looping through 20 results each page
                while nextPage:
                    count = -1  # in case web element is lost
                    # used to check if business details finished loading
                    previousTitle = None
                    for entry in driver.find_elements(
                        "xpath", '//div[@jsname="GZq3Ke"]'
                    ):
                        count += 1

                        row = []
                        try:
                            entry.click()
                        except StaleElementReferenceException:
                            driver.find_elements("xpath", '//div[@jsname="GZq3Ke"]')[
                                count
                            ].click()
                        WebDriverWait(driver, 5).until(
                            lambda x: driver.find_element(
                                "xpath", "//h2[@data-attrid='title']"
                            )
                            != previousTitle
                        )  # check if details finished loading
                        try:
                            row.append(
                                driver.find_element(
                                    "xpath", "//h2[@data-attrid='title']"
                                ).text
                            )  # name
                            previousTitle = driver.find_element(
                                "xpath", "//h2[@data-attrid='title']"
                            )
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                        try:
                            row.append(
                                driver.find_element(  # website
                                    "xpath", "//div[text()='Website']/.."
                                ).get_attribute("href")
                            )
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                        try:
                            row.append(
                                driver.find_element(  # stars
                                    "xpath",
                                    "//div[@data-attrid='kc:/local:lu attribute list']/div/div/div/span[1]",
                                ).text
                            )
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                        try:
                            row.append(
                                driver.find_element(  # review count
                                    "xpath",
                                    "//span[contains(text(),'Google reviews')]",
                                ).text
                            )
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                        try:
                            row.append(
                                driver.find_element(  # category
                                    "xpath",
                                    "//span[@class='YhemCb'][last()]",
                                ).text
                            )
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                        try:
                            row.append(
                                driver.find_element(  # phone
                                    "xpath",
                                    "//*[contains(@*,'Call phone')]",
                                ).text
                            )
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                        try:
                            address = driver.find_element(  # address
                                "xpath",
                                "//*[contains(text(),'Address')]/../../*[2]",
                            ).text.split(",")
                            try:
                                provincePostalCode = address.pop()
                                city = address.pop()
                            except IndexError:
                                city = ""
                                provincePostalCode = ""

                            row.append(", ".join(address))
                            row.append(city)
                            row.append(provincePostalCode)

                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")
                            row.append("N/A")
                            row.append("N/A")

                        thirdpartyordering = []
                        try:
                            for entry in driver.find_elements(
                                "xpath", "//div[@data-attrid='kc:/local:order_food']//a"
                            ):  # 3rd party ordering
                                thirdpartyordering.append(entry.text)
                            row.append(", ".join(thirdpartyordering))
                        except (NoSuchElementException, StaleElementReferenceException):
                            row.append("N/A")

                        row.append(
                            datetime.datetime.now().strftime(
                                f"%Y-%m-%d %H:%M:%S"
                            )  # Timestamp
                        )

                        print(row)
                        print()

                        spreadsheet = (
                            service.spreadsheets()
                            .values()
                            .append(
                                spreadsheetId=spreadsheetId,
                                range=updatedRange,
                                valueInputOption="RAW",
                                body={"values": [row]},
                            )
                            .execute()
                        )

                        rowNum += 1
                        updatedRange = f"{csvRow['city']}!I{rowNum}"

                    try:
                        driver.find_element(  # enter data while there is next page
                            "xpath", "//span[contains(text(),'Next')]"
                        ).click()
                    except NoSuchElementException:
                        print(
                            f"Reached the last result on the last page of query: {businesstype} {csvRow['city']}"
                        )
                        nextPage = False

                    time.sleep(3)


if __name__ == "__main__":
    main()
