import re 
import os 
import sys 
PROJ_ROOT_DIR= os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PROJ_ROOT_DIR)

import requests 
import urllib.request
from urllib import parse
from bs4 import BeautifulSoup
import bs4
from dataclasses import asdict
try:

  from common.EsCommon import EsCommon
  from skeleton.Template import Template
  from skeleton.PlayerTemplete import PlayerTemplate
except ImportError as err:
  print(err)
  exit(1)

'''
@author JunHyeon.Kim
@date 20221127
'''
class AIPepp(Template, EsCommon):
  ''''''
  def __init__(self) -> None:
    global PROJ_ROOT_DIR 
    EsCommon.__init__(self)
    
    self._char_delimiters = "년", "월", "일"
    self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

    self._flag: str = "aip"
    self._base_url: str = "http://www.aipeppers.kr"
    self._url_path: str = "/team_sub1.php"
    self._player_url_list: list[str] = list() 
    self._aipepp_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"img/{self._flag}")

  def get_url(self):
    '''
    '''
    response: requests.models.Response = requests.get(f"{self._base_url}{self._url_path}")
    #print(f"type: {type(response)}")

    if response.status_code == 200:
      bs_object = BeautifulSoup(response.text, "html.parser")
      team_list_ui = bs_object.select_one("ul.teamListUl")

      li_tags:list = team_list_ui.select("li")

      for l in li_tags:
        href_url:str = l.select_one("a").attrs["href"]
        self._player_url_list.append(self._base_url + href_url)

    else: 
      ''''''