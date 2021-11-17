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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import numpy as np
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

    # get the data into 4 different array and combine into one 2D array
    storeUrl = np.array(service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!E2:E").execute()['values'])
    storeName = np.array(service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!I2:I").execute()['values'])
    storeProvince = np.array(service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!L2:L").execute()['values'])
    messageType = np.array(service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range="Burnaby!W2:W").execute()['values'])

    # thiscombine the arrays into a 2D array, each row has an array with 4 elements
    storesInfo = np.column_stack(
        (storeUrl, storeName, storeProvince, messageType))
    print(storesInfo)

    driver.get("https://www.instagram.com/")
    driver.find_element('name', 'username').send_keys(name)
    driver.find_element('name', 'password').send_keys(password)
    driver.find_element('xpath', "//*[contains(text(), 'Log In')]").click()
    driver.find_element('xpath', "//button[contains(text(), 'Not now')]"
                        ).click()
    driver.find_element('xpath', "//button[contains(text(), 'Not Now')]"
                        ).click()

    for details in storesInfo:
        if(details[0] != 'N/A'):
            driver.get(details[0])
            driver.find_element(
                'xpath', "//div[contains(text(), 'Message')]").click()
            f = open(f"message-{details[3]}.txt", "r")
            message = f.read()
            f.close()
            message = message.replace("{store-name}", details[1])
            if'British Columbia' not in details[2]:
                message = message.replace("{Burnaby-based}", "Vancouver-based")
            else:
                message = message.replace("{Burnaby-based}", "Burnaby-based")
            for line in message.split('\n'):
                driver.find_element(
                    'xpath', "//textarea[@placeholder]").send_keys(line)
                ActionChains(driver).key_down(Keys.SHIFT).key_down(
                    Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
            driver.find_element(
                'xpath', "//textarea[@placeholder]").send_keys(Keys.ENTER)

    driver.close()


if __name__ == '__main__':
    main()
