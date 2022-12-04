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
class GSVoll(Template, EsCommon):
  
  def __init__(self) -> None:
    global PROJ_ROOT_DIR 
    EsCommon.__init__(self)
    
    self._char_delimiters = "년", "월", "일"
    self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

    self._flag: str = "gsv"
    self._base_url: str = "https://www.gsvolleyball.com"
    self._url_path: str = "/team/player"
    self._player_url_list: list[str] = list() 
    self._gsvoll_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"img/{self._flag}")

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

  def player_detail_information(self):
    '''
    :param:
    :return:
    '''
    if len(self._player_url_list) > 0:
      for u in self._player_url_list:

        player_info = asdict(
            PlayerTemplate(
              player_name= "", 
              player_number= 0,
              player_position= "",
              player_detail_url= None,
              player_height= 0,
              player_birthday= {
                "year": None
                ,"month": None
                ,"day": None  
              },
              player_school = [], 
              player_img_path = ""
            )
        )

        player_info["player_detail_url"] = u

        response = requests.get(u)

        if response.status_code == 200:
          bs_object = BeautifulSoup(response.text, "html.parser")
          player_profile:bs4.element.Tag = bs_object.select_one("div.teamDetailWrap")
          team_detail_wrap = player_profile

          player_profile = player_profile.select_one("div.tDetailInfo")
          tdi_1 = player_profile.select_one("div > div.tdi_1")
          div_tags:list = tdi_1.select("div")

          for d in div_tags:
            dl_tag = d.select_one("dl")
            dt_tag = str(dl_tag.select_one("dt").text).strip()
            if dt_tag == "number":
              player_number:int = int(str(dl_tag.select_one("dd.tDetailNumber").text).lstrip("0"))
              player_info["player_number"] += player_number
            elif dt_tag == "position":
              player_position:str = str(dl_tag.select_one("dd.tDetailPosition").text).strip()
              player_info["player_position"] += player_position
          
          tdi_2 = player_profile.select_one("div > div.tdi_2")
          player_name = str(tdi_2.select_one("strong").text).strip()
          player_info["player_name"] += player_name

          tdi_3 = player_profile.select_one("div.tdi_3")
          dl_tags :list = tdi_3.select("dl")

          for dl in dl_tags:
            k = str(dl.select_one("dt").text).strip()
            
            if k == "생년월일":
              v = str(dl.select_one("dd").text).replace(" ", "")
              player_birthday: list[str] = [e for e in re.split(self._regex_pattern, v) if e]
              player_info["player_birthday"]["year"] = int(player_birthday[0])
              player_info["player_birthday"]["month"] = int(str(player_birthday[1]).lstrip("0"))
              player_info["player_birthday"]["day"] = int(str(player_birthday[2]).lstrip("0"))
            elif k == "출신교":
              v = str(dl.select_one("dd").text).replace(" ", "")
              player_school:list[str] = [sch for sch in v.split("-") if sch]
              player_info["player_school"].extend(player_school)
            elif k == "신장":
              v = int(str(dl.select_one("dd").text).rstrip("cm"))
              player_info["player_height"] += v
          
          # ==============================================================================
          img_tag = team_detail_wrap.select_one(
            "div.tDetailPhotoWrap.photo1" +\
            " > " +\
            "img"
          )

          img_file_path:str = f"{self._gsvoll_photo_path}/{player_info['player_name']}.png"

          try:
            
            urllib.request.urlretrieve(
              img_tag.attrs["src"],
              img_file_path)
          except:
            print(f"img download fail")
            pass 
          else: 
            player_info["player_img_path"] += img_file_path
          # ==============================================================================
          print(player_info)

        else:
          ''''''


if __name__ == "__main__":
  o = GSVoll()
  o.get_url()
  o.player_detail_information()