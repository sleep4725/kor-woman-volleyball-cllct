import dataclasses
import re
import os
import sys
PROJ_ROOT_DIR= os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PROJ_ROOT_DIR)

from concurrent.futures import ThreadPoolExecutor
import requests
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

import urllib.request as req

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import bs4
from dataclasses import asdict

try:
    from engine.NewChrome import *
    from engine.ChromeSelEngine import ChromeSelEngine
    from es.EsClient import EsClient
    from common.EsCommon import EsCommon
    from skeleton.Template import Template
    from skeleton.PlayerTemplete import PlayerTemplate
except ImportError as err:
  print(err)
  exit(1)

"""
@author JunHyeon.Kim
@date 20221205
"""
class PlayerPosition:

    POSITION = {
        "LIBERO": "L"
        , "OUTSIDE HITTER": "OH"
        , "SETTER": "S"
        , "MIDDLE BLOCKER": "MB"
    }

class PinkSpider(EsCommon):
    ''''''
    def __init__(self, deploy: str)-> None:
        global PROJ_ROOT_DIR
        EsCommon.__init__(self)
        self._es_client: Elasticsearch = EsClient.get_es_client(deploy=deploy)

        self._char_delimiters = "년", "월", "일"
        self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

        self._flag: str = "pink"
        self._team_name: str = "흥국생명"
        self._base_url: str = "https://www.pinkspiders.co.kr"
        self._url_team_path: str = "team"
        self._url_player_list_path: str = "player_list.php"
        self._player_url_list: list[str] = list()
        self._aipepp_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"img/{self._flag}")

    def get_url(self):
        '''
        :param:
        :return:
        '''
        response: requests.models.Response = requests.get(
            "{base_url:s}/{team_path:s}/{player_list_path:s}".format(
                        base_url = self._base_url,
                        team_path = self._url_team_path,
                        player_list_path = self._url_player_list_path
                )
        )

        if response.status_code == 200:
            bs_object: bs4.element.Tag = BeautifulSoup(response.text, "html.parser")
            player: bs4.element.Tag = bs_object.select_one("div.row_group.col_3.player_list")

            player_list: bs4.element.ResultSet = player.select("a.col.frame_g")
            for p in player_list:
                p: bs4.element.Tag = p
                player_url: str = "{base_url:s}/{team_path:s}{player_url:s}&flag=get_player_data".format(
                    base_url = self._base_url,
                    team_path = self._url_team_path,
                    player_url = str(p.attrs["href"]).lstrip(".")
                )
                self._player_url_list.append(player_url)
        else:
            ''''''
        response.close()

def get_information(
        frame_g: WebElement
    )-> dict:
    '''

    '''
    txt_g :WebElement = frame_g.find_element(By.CSS_SELECTOR, "span.txt_g")

    # 1. 선수-포지션
    position :WebElement = txt_g.find_element(By.CSS_SELECTOR, "span.col_pink")
    player_position :str = PlayerPosition.POSITION[str(position.text).strip()]

    # 2. 선수-백넘버
    back_number :WebElement = txt_g.find_element(By.CSS_SELECTOR, "span.player_no")
    player_back_number :int = int(str(back_number.text).strip().lstrip("NO.").lstrip("0"))

    # 3. 선수-이름
    name :WebElement = txt_g.find_element(By.CSS_SELECTOR, "strong")
    player_name :str = str(name.text).strip()

    return {
        "player_name": player_name
        , "player_number": player_back_number
        , "player_position": player_position
    }

def get_information_2(
        frame_g: WebElement
    ):
    '''

    '''
    ul_tag :WebElement = frame_g.find_element(By.CSS_SELECTOR, "ul")
    li = ul_tag.find_elements("li")
    print(f"li type : {type(li)}")

def crwl_player(
        u: str,
        chrome_driver: WebDriver
    )-> str:
    '''
    :param u:
    :param chrome_driver:
    '''
    chrome_driver.get(u)
    chrome_driver.implicitly_wait(20)
    chrome_driver.find_element(By.CSS_SELECTOR, "div.player_profile > div.wrap.row_group")
    frame_g :WebElement = chrome_driver.find_element(By.CSS_SELECTOR, "div.col.frame_g")
    player_info_1 :dict = get_information(frame_g=frame_g)
    get_information_2(frame_g=frame_g)
    img = chrome_driver.find_element(By.CSS_SELECTOR, "div.img_group.col > img")
    img_url = img.get_attribute("src")
    print(img_url)
    chrome_driver.quit()

    return player_info_1

if __name__ == "__main__":
    o = PinkSpider(deploy="local")
    o.get_url()

    if len(o._url_player_list_path) > 0:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    crwl_player,
                    u,
                    get_chrome_driver()
                ) for u in o._player_url_list
            ]

            for f in futures:
                print(f.result())



