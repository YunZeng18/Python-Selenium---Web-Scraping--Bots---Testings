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

import traceback
import logging


# download chrome web driver zip file according to your chrome version and Operating System
# https://sites.google.com/chromium.org/driver/
# extract the zip to a directory for later use
PATH = "/lib/chromedriver"

# instagram login
name = config("username")
password = config("pass")


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

    businessNames = service.spreadsheets().values().get(
        spreadsheetId="1udPHPUowWRyS5tv4lu2TXGNkHYn56lV4QKdn2MNzamk", range="Sheet1!I2:I9").execute()
    print(businessNames["values"])

    driver = webdriver.Chrome(PATH)
    driver.implicitly_wait(4)
    driver.get("https://www.instagram.com/")

    try:

        driver.find_element('name', 'username').send_keys(name)
        driver.find_element('name', 'password').send_keys(password)
        driver.find_element('xpath', "//*[contains(text(), 'Log In')]").click()

        for business in businessNames["values"]:

            # remove spaces to improve search
            queryString = '@'+business[0]

            search = driver.find_element(
                'xpath', "//input[@aria-label=\"Search Input\"]")
            search.clear()
            search.send_keys(queryString)

            # the div element that contains the search results
            results = search.find_element('xpath', "//*[@aria-hidden]")

            try:
                results.find_element('xpath',
                                     "//*[contains(text(), 'No results found.')]")  # this will raise exception if the results aren't empty
                print(f'search query "{queryString}": no results')

            except NoSuchElementException:

                topResult = results.find_element(
                    'xpath', "div[2]/div/div/a").get_attribute("href")

                # Check the first result's link string. If it has "explore" in its path, it's not a store page.
                if("explore" not in topResult):
                    print(f'search query "{queryString}": {topResult}')
                    driver.get(topResult)

                else:
                    print(f'search query "{queryString}": bad results')

        while True:
            pass
    except Exception:
        logging.error(traceback.format_exc())
        driver.quit()


if __name__ == '__main__':
    main()
