import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_chrome_driver():
    co = Options()
    co.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    driver = webdriver.Chrome(options=co)
    return driver