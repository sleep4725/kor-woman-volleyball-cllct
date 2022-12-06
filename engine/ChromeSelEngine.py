from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

"""
"""
class ChromeSelEngine:

    @classmethod
    def get_chrome_driver(cls):
        '''

        '''
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")

        chrome_driver: WebDriver = webdriver.Chrome(
            executable_path="/Users/kimjunhyeon/Downloads/chrome-driver/chromedriver",
            chrome_options=options
        )

        return chrome_driver

