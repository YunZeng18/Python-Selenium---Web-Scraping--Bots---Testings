from __future__ import print_function

# for accessing google sheet
# $ sudo pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# access local development environment variables from .env file
# $ sudo pip3 install python-decouple
from decouple import config

# install selenium package
# $ sudo pip3 install selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

# $ sudo pip3 install numpy
# for pairing two arrays into one
import numpy as np

import datetime
import sys
import traceback
import logging


# download chrome web driver zip file according to your chrome version and Operating System
# https://sites.google.com/chromium.org/driver/
# extract the zip to a directory for later use
PATH = "/lib/chromedriver"

option = Options()

option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")

# Pass the argument 1 to allow and 2 to block
option.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 1
})

driver = webdriver.Chrome(chrome_options=option, executable_path=PATH)
driver.implicitly_wait(2)


# facebook login
name = config("FacebookUsername")
password = config("FacebookPass")

spreadsheetId = config("spreadsheetId")


def main():

    # If modifying these scopes, delete the file token.json.
    # https://developers.google.com/sheets/api/guides/authorizing
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # get the business names in an array for search
    businessNames = np.array(service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!I2:I").execute()["values"])
    streetAddress = np.array(service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!J2:J").execute()["values"])

    # use numpy to combine two arrays into pairs in one array
    queries = np.column_stack((businessNames, streetAddress))

    # starting point in the google sheet
    rowNum = 2
    updatedRange = f"Burnaby!F{rowNum}:H{rowNum}"

    try:

        driver.get("https://www.facebook.com/")
        driver.find_element('id', 'email').send_keys(name)
        driver.find_element('id', 'pass').send_keys(password)
        driver.find_element('name', 'login').click()

        for entry in queries:
            print(entry)
            row = []

            driver.get(f"https://www.facebook.com/search/places/?q={entry}")

            try:
                facebookpage = driver.find_element(
                    'xpath',
                    "//*[contains(@aria-label, '1.')]"
                ).get_attribute("href")
                try:
                    driver.find_element(
                        'xpath',
                        "//span[contains(text(),'Disagree')]"
                    ).click()
                except NoSuchElementException:
                    pass
                driver.find_element(
                    'xpath',
                    "//*[contains(@aria-label, 'Like')]"
                ).click()
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                row = [date, '', facebookpage]
            except NoSuchElementException:
                row = ['N/A', '', 'N/A']

            print(row)
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheetId,
                range=updatedRange,
                valueInputOption="RAW",
                body={'values': [row]}).execute()
            rowNum += 1
            updatedRange = f"Burnaby!F{rowNum}:H{rowNum}"

        sys.exit()
    except Exception:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main()
