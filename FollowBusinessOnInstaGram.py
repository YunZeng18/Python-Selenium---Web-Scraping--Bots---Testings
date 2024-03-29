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
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

import time
import datetime
import sys
import traceback
import logging


# download chrome web driver zip file according to your chrome version and Operating System
# https://sites.google.com/chromium.org/driver/
# extract the zip to a directory for later use
s = Service("/lib/chromedriver")
driver = webdriver.Chrome(service=s)
driver.implicitly_wait(2)

# instagram login
name = config("InstagramUsername")
password = config("InstagramPass")

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
    # instagram doesn't support searching with multiple creteria combined together
    # best results is @ + business name
    businessNames = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!I2:I").execute()

    # input starting point in the google sheet
    rowNum = 2
    updatedRange = f"Burnaby!C{rowNum}:E{rowNum}"

    try:
        # beginning of scripts to navigate instagram
        driver.get("https://www.instagram.com/")
        driver.find_element('name', 'username').send_keys(name)
        driver.find_element('name', 'password').send_keys(password)
        driver.find_element('xpath', "//*[contains(text(), 'Log In')]").click()

        for business in businessNames["values"]:

            print(business)

            # construct the rows of data to enter into google sheet
            row = []

            # @ symbol filter out hash tag and location results
            queryString = '@'+business[0]
            search = driver.find_element(
                'xpath', "//input[contains(@*,'Search')]")
            search.clear()
            search.send_keys(queryString)

            # the div element that contains the search results
            results = search.find_element('xpath', "//*[@aria-hidden]")

            try:
                time.sleep(1)

                topResult = results.find_element(
                    'xpath', "div[2]/div/div/a")  # this will raise exception if the results are empty
                pageURL = topResult.get_attribute("href")
                print(f'search query "{queryString}": {pageURL}')
                driver.get(pageURL)
                try:
                    driver.find_element(
                        'xpath', "//button[contains(text(),'Follow')]").click()
                    date = datetime.datetime.now().strftime(f"%Y-%m-%d")
                    row = [date, '', pageURL]
                except NoSuchElementException:
                    row = ['N/A', '', pageURL]

            except NoSuchElementException:
                print(f'search query "{queryString}": no results')
                row = ["N/A", "", "N/A"]

            service.spreadsheets().values().update(
                spreadsheetId=spreadsheetId,
                range=updatedRange,
                valueInputOption="RAW",
                body={'values': [row]}).execute()
            rowNum += 1
            updatedRange = f"Burnaby!C{rowNum}:E{rowNum}"

        print('end of queries')
        driver.close()
        sys. exit()
    except Exception:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main()
