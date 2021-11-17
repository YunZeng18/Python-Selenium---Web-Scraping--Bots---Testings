# How to run the scripts

install python on Ubuntu
$ sudo apt install python3-pip

install selenium and various other packages
$ pip3 install selenium

for accessing google sheet https://developers.google.com/sheets/api/quickstart/python
$ sudo pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

access local development environment variables from .env file
$ sudo pip3 install python-decouple

for pairing two arrays into one
$ sudo pip3 install numpy

download chrome web driver zip file according to your chrome version and system
https://sites.google.com/chromium.org/driver/
extract the zip to a directory for later use

create .env file and define the value for the following
InstagramUsername=
InstagramPass=
FacebookUsername=
FacebookPass=
spreadsheetId=

create a project on google cloud console and download credential files. rename it to credential.json and save in the same directory.

craw data into google sheet run
$ python3 crawler2.py

follow businesses on instagram
$ python3 FollowBusinessOnInstaGram.py

follow businesses on facebook
$ python3 FollowBusinessOnFaceBook.py

# Notes

## crawler.py

first attempt to get results from google map. I thought it would be easier but google ends up limiting you from getting more than 60 results on the same query. So for the same query like "restaurants in burnaby" you will only get 3 calls to the https://maps.googleapis.com/maps/api/place/textsearch/json?query={businesstype}%20{location}&key={key}&pagetoken={nextPageToken} and there would be no more nextPageToken after 3 calls that return 20 results each.

## crawler2.py

This script directly navigates through the google.com and crawl the results of restaurants in burnaby. You can change the query to by changing the variables businesstype and location. Google scramble all the tag names and ID so it was hard initially to get the elements until I discover the proper use of xpath in selenium package.
I also discover that you can test your xpath in the chrome dev element tag by using ctl + F. This saves a lot of time.

## FollowBusinessOnInstaGram.py

I struggle a lot with how to filter down the search result to the store page because the search engine isn't that good on instagram. I discovered you can add @ symbol to effectively filter out location and hashtag results. However, I realize there isn't a reliable way to determine if the store page is the one you want because instagram doesn't support sophisticated search filters. So I default to look at the first one on the result list and it usually returns a good match most of the time.

## FollowBusinessOnFaceBook.py

The search engine on facebook supports filter by address so it was always the top result if it matches. However, facebook detects your repetitive follow activity and stops you from following too many pages in a row with a popup.
I tried to use script to click through the pop up that stops you from liking pages. But after 30 or so requests it just log you out and send you to login screen after 50 or so entries. None of the pages previously liked was actually liked when the pop up was in effect anyways. Now the new account is actually disabled within 30 days if i don't do something about it.

## sendMessageOnInstagram.py

replace \n in instagram text area element so it doesn't send message every new line.

## Valuables

-Add @ prefix on instagram search to filter results down to instagram user accounts so it excludes location and hashtag results.
-xpath search syntax
-press ctrl + f in element tabs of chrome dev to test xpath
-selenium api
-google sheet api
