import re 
import os 
import sys 
PROJ_ROOT_DIR= os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PROJ_ROOT_DIR)

import requests 
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import urllib.request
from urllib import parse
from bs4 import BeautifulSoup
import bs4
from elasticsearch import Elasticsearch
from dataclasses import asdict

try:

  from es.EsClient import EsClient
  from common.EsCommon import EsCommon
  from common.EsIndex import EsIndex
  from skeleton.Template import Template
  from skeleton.PlayerTemplete import PlayerTemplate
except ImportError as err:
  print(err)
  exit(1)

'''
GS칼텍스
@author JunHyeon.Kim
@date 20221127
'''
class GSVoll(Template, EsCommon):
  
  def __init__(self, deploy: str) -> None:
    global PROJ_ROOT_DIR 
    EsCommon.__init__(self)
    self._es_client: Elasticsearch = EsClient.get_es_client(deploy=deploy)

    self._char_delimiters = "년", "월", "일"
    self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

    self._flag: str = "gsv"
    self._team_name: str = "지에스칼텍스"
    self._base_url: str = "https://www.gsvolleyball.com"
    self._url_path: str = "/team/player"
    self._player_url_list: list[str] = list()
    self._img_file_path: str = f"img/{self._flag}" 
    self._gsvoll_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"web/static/{self._img_file_path}")

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

  def get_player_position(self, player_detail_info: bs4.element.Tag)\
        -> str:
    '''
    선수 포지션
    :param player_detail_info:
    :return:
    '''
    return str(player_detail_info.text).strip()

  def get_player_number(self, player_detail_info: bs4.element.Tag)\
        -> int:
    '''
    선수 백넘버
    :return:
    '''
    return int(str(player_detail_info.text).lstrip("0"))

  def get_player_name(self, player_detail_info: bs4.element.Tag)\
          -> str:
    '''
    선수 이름
    :return:
    '''
    return str(player_detail_info.text).strip()

  def get_player_birthday(self, birthday: str)\
          -> list[int]:
    '''
    선수 생일
    :return:
    '''
    return [
      int(str(e).lstrip("0").strip()) for e in re.split(self._regex_pattern, birthday) if e
    ]

  def get_player_school(self, school: str)\
          -> list[str]:
    '''
    :param l:
    :param result:
    :return:
    '''
    return [str(s).strip() for s in school.split("-") if s]

  def get_player_height(self, height: str) \
          -> float:
    '''
    :param:
    :return:
    '''
    return float(height.rstrip("cm"))

  def download_player_img(self, 
                          img_file_path: str,
                          player_detail_info: bs4.element.Tag)\
          -> bool:
    '''
    '''
    try:
      
      urllib.request.urlretrieve(
        player_detail_info.attrs["src"],
        img_file_path)
    except:
      print(f"img download fail")
      return False
    else:
      return True
    
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
              player_team_name=self._team_name,
              player_number= 0,
              player_position= "",
              player_detail_url= None,
              player_height= .0,
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
          player_profile :bs4.element.Tag= bs_object.select_one("div.teamDetailWrap")
          team_detail_wrap :bs4.element.Tag= player_profile

          player_profile = player_profile.select_one("div.tDetailInfo")
          tdi_1 = player_profile.select_one("div > div.tdi_1")
          div_tags:list = tdi_1.select("div")

          for d in div_tags:
            dl_tag = d.select_one("dl")
            dt_tag = str(dl_tag.select_one("dt").text).strip()
            
            ## 선수 백넘버
            if dt_tag == "number":
              player_number :int= self.get_player_number(player_detail_info= dl_tag.select_one("dd.tDetailNumber"))
              player_info["player_number"] += player_number
            
            ## 선수 포지션  
            elif dt_tag == "position":
              player_position :str= self.get_player_position(player_detail_info= dl_tag.select_one("dd.tDetailPosition"))
              player_info["player_position"] += player_position
          
          tdi_2 = player_profile.select_one("div > div.tdi_2")
          
          ## 선수 이름  
          player_name :str= self.get_player_name(player_detail_info= tdi_2.select_one("strong"))
          player_info["player_name"] += player_name

          tdi_3 = player_profile.select_one("div.tdi_3")
          dl_tags :list = tdi_3.select("dl")

          for dl in dl_tags:
            k = str(dl.select_one("dt").text).strip()
            
            if k == "생년월일":
              birthday_list :list[int]= self.get_player_birthday(birthday= str(dl.select_one("dd").text).replace(" ", ""))
              player_info["player_birthday"]["year"] = birthday_list[0]
              player_info["player_birthday"]["month"] = birthday_list[1]
              player_info["player_birthday"]["day"] = birthday_list[2]
              
            elif k == "출신교":
              school_list :list[str]= self.get_player_school(school=str(dl.select_one("dd").text).replace(" ", ""))
              player_info["player_school"].extend(school_list)
              
            elif k == "신장":
              player_height: float = self.get_player_height(height= str(dl.select_one("dd").text))
              player_info["player_height"] += player_height
          # ==============================================================================
          # Image-download-start
          img_tag = team_detail_wrap.select_one(
            "div.tDetailPhotoWrap.photo1" +\
            " > " +\
            "img"
          )
          
          img_file_path :str= f"{self._gsvoll_photo_path}/{player_info['player_name']}.png" 
          result :bool= self.download_player_img(img_file_path= img_file_path, player_detail_info= img_tag)
          if result:
            player_info["player_img_path"] += f"{self._img_file_path}/{player_info['player_name']}.png"
          # Image-download-end 
          # ==============================================================================
          print(player_info)
          self._es_action.append(
            {
              "_index": EsIndex.KOR_WOM_INDEX
              , "_id": f"{self._team_name}_{player_info['player_name']}_{player_info['player_number']}"
              , "_source": player_info
            }
          )
        else:
          ''''''

  def document_bulk_insert(self):
      '''
      :param:
      :return:
      '''
      if len(self._es_action) > 0:
          self.bulk_insert(es_client= self._es_client)
      else:
          print("적재할 데이터가 없습니다.")

if __name__ == "__main__":
  o = GSVoll(deploy="local")
  o.get_url()
  o.player_detail_information()
  o.document_bulk_insert()