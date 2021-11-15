# install python on Linux(I am using Ubuntu)
# $ sudo apt install python3-pip

# for accessing google sheet
# $ sudo pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
from __future__ import print_function
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path

# access local development environment variables from .env file
# $ sudo pip3 install python-decouple
from decouple import config

# install selenium package
# $ sudo pip3 install selenium
from selenium import webdriver
from selenium.common import exceptions
from selenium.common.exceptions import NoSuchElementException

import time
import datetime
import sys
import traceback
import logging


# download chrome web driver zip file according to your chrome version and Operating System
# https://sites.google.com/chromium.org/driver/
# # extract the zip to a directory for later use
PATH = "/lib/chromedriver"  # this the chrome driver file is
driver = webdriver.Chrome(PATH)
driver.implicitly_wait(4)

# need to register on the google maps platform and create a project to get the API Key, this makes crawling easier
key = config('GoogleMapAPIKey')

businesstype = "restaurants"
location = "burnaby"


def main():

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

    # create a new Google sheet
    spreadsheet = {
        'properties': {
            'title': f'{businesstype} in {location}'
        }
    }
    spreadsheet = service.spreadsheets().create(
        body=spreadsheet, fields='spreadsheetId').execute()

    spreadsheetId = spreadsheet.get('spreadsheetId')
    ###

    # enter column headings in the first row
    headings = [
        [
            "name", "website", "stars", "review count", "category", "phone", "address", "3rd party ordering", "Timestamp"
        ]
    ]
    body = {
        'values': headings
    }
    spreadsheet = service.spreadsheets().values().append(spreadsheetId=spreadsheetId,
                                                         range="A1",        valueInputOption="RAW", body=body).execute()

    updatedRange = spreadsheet['updates']['updatedRange']
    ###

    driver.get(
        f"https://www.google.com/search?q={businesstype}%20in%20{location}")

    driver.find_element('xpath', "//span[contains(text(),'View all')]").click()

    try:
        while (True):
            results = driver.find_elements(
                'xpath', '//div[@data-record-click-time="false"]')
            page = []
            for entry in results:
                row = []
                print(entry.get_attribute('id'))
                entry.click()
                time.sleep(1)
                try:
                    row.append(driver.find_element(  # name
                        'xpath', "//h2/*").text)
                except NoSuchElementException:
                    row.append('N/A')
                try:
                    row.append(driver.find_element(  # website
                        'xpath', "//div[contains(text(), 'Website')]/..").get_attribute("href"))
                except NoSuchElementException:
                    row.append('N/A')
                try:
                    row.append(driver.find_element(  # stars
                        'xpath', "//div[@data-attrid='kc:/local:lu attribute list']/div/div/div/span[1]").text)
                except NoSuchElementException:
                    row.append('N/A')
                try:
                    row.append(driver.find_element(  # review count
                        'xpath', "//div[@data-attrid='kc:/local:lu attribute list']/div/div/div/span[2]").text)
                except NoSuchElementException:
                    row.append('N/A')
                try:
                    row.append(driver.find_element(  # category
                        'xpath', "//div[@data-attrid='kc:/local:lu attribute list']/div[2]/div/span[last()]").text)
                except NoSuchElementException:
                    row.append('N/A')
                try:
                    row.append(driver.find_element(  # phone
                        'xpath', "//span[contains(@aria-label,'Call phone')]").text)
                except NoSuchElementException:
                    row.append('N/A')
                try:
                    row.append(driver.find_element(  # address
                        'xpath', "//*[contains(text(),'Address')]/../../*[2]").text)
                except NoSuchElementException:
                    row.append('N/A')

                thirdpartyordering = []
                for entry in driver.find_elements(  # 3rd party ordering
                        'xpath', "//div[@data-attrid='kc:/local:order_food']//a"):
                    thirdpartyordering.append(entry.text)
                row.append(', '.join(thirdpartyordering))

                row.append(datetime.datetime.now().strftime(  # Timestamp
                    f"%Y-%m-%d %H:%M:%S"))

                page.append(row)

                print(row)
                print()

            spreadsheet = service.spreadsheets().values().append(
                spreadsheetId=spreadsheetId, range=updatedRange,
                valueInputOption="RAW", body={
                    'values': page
                }).execute()

            updatedRange = spreadsheet['updates']['updatedRange']

            try:
                driver.find_element(  # enter data while there is next page
                    'xpath', "//span[contains(text(),'Next')]").click()
            except NoSuchElementException:
                print('reached last page of results')
                driver.close()
                sys. exit()
            time.sleep(4)

    except exceptions:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main()
