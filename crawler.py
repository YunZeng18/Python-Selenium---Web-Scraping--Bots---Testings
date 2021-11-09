# install python on Linux(I am using Ubuntu)
# $ sudo apt install python3-pip

# install selenium package
# $ pip3 install selenium
from selenium import webdriver

# download chrome web driver zip file according to your chrome version and system
# https://sites.google.com/chromium.org/driver/
# extract the zip to a directory for later use
PATH = "/lib/chromedriver"  # this where the chrome driver file is

driver = webdriver.Chrome(PATH)

driver.get("http://yun-zeng.net")

# in the directory run the program $ python3 crawler.py
