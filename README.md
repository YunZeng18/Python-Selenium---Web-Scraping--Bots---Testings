install python on Ubuntu
$ sudo apt install python3-pip

install selenium package
$ pip3 install selenium

download chrome web driver zip file according to your chrome version and system
https://sites.google.com/chromium.org/driver/
extract the zip to a directory for later use

create .env file for the following
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

### notes

crawler.py query google map api to get results, unfortunately Google limits you from getting more than 60 results on the same query

crawler2.py crawls google search results directly

hardest challenge: determine which search result is the one representing the store page
learn xpath search syntax
add @ prefix to filter results by category of instagram users
press ctrl + f in element tabs of chrome dev to test xpath
