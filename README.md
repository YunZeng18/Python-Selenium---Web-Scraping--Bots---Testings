install python on Ubuntu
$ sudo apt install python3-pip

install selenium package
$ pip3 install selenium

download chrome web driver zip file according to your chrome version and system
https://sites.google.com/chromium.org/driver/
extract the zip to a directory for later use

create .env file define username and pass variables for instagram login
download

craw data into google sheet run $ python3 crawler2.py
search business on IG and follow if they have a store page $ python3 FollowBusinessOnInstaGram.py

### notes

crawler.py query google map api to get results, unfortunately Google limits you from getting more than 60 results on the same query

crawler2.py crawls google search results directly

hardest challenge: determine which search result is the one representing the store page
learn xpath search syntax
add @ prefix to filter results by category of instagram users
press ctrl + f in element tabs of chrome dev to test xpath
