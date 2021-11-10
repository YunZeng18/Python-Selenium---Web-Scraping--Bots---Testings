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

import requests  # http requests


# download chrome web driver zip file according to your chrome version and Operating System
# https://sites.google.com/chromium.org/driver/
# # extract the zip to a directory for later use
PATH = "/lib/chromedriver"  # this the chrome driver file is

driver = webdriver.Chrome(PATH)

# need to register on the google maps platform and create a project to get the API Key, this makes crawling easier
key = config('GoogleMapAPIKey')

businesstype = "restaurants"
location = "burnaby"


def main():
    # for more query options such as radius and location:
    # https://developers.google.com/maps/documentation/places/web-service/search-text
    query = requests.get(
        f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={businesstype}%20{location}&key={key}").json()

    nextPageToken = query.get("next_page_token")

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

    # Call the Google Sheets API

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
            "name", "business_status", "website", "formatted_phone_number", "formatted_address", "weekday_text"
        ]
    ]
    body = {
        'values': headings
    }
    spreadsheet = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range="A1",
                                                         valueInputOption="RAW", body=body).execute()
    updatedRange = spreadsheet.get('updatedRange')
    ###

    # enter data while there is next page
    while nextPageToken != None:
        data = []
        for business in query['results']:
            detail = requests.get(
                f"https://maps.googleapis.com/maps/api/place/details/json?&place_id={business['place_id']}&fields=formatted_phone_number,opening_hours,website&key={key}").json()

            row = []
            for heading in headings[0]:
                if (heading in business):
                    row.append(business[heading])
                elif(heading in detail["result"]):
                    row.append(detail["result"][heading])
                elif(heading == "weekday_text" and "opening_hours" in detail["result"] and "weekday_text" in detail["result"]["opening_hours"]):
                    row.append(" | ".join(
                        detail["result"]["opening_hours"]["weekday_text"]))
                else:
                    row.append("-")

            data.append(row)

        body = {
            'values': data
        }

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheetId, range=updatedRange,
            valueInputOption="RAW", body=body).execute()

        nextPageToken = query.get("next_page_token")
        query = requests.get(
            f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={businesstype}%20{location}&key={key}&pagetoken={nextPageToken}").json()

    ###


if __name__ == '__main__':
    main()
