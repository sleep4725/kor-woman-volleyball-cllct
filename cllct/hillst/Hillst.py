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
from elasticsearch import Elasticsearch
from dataclasses import asdict
try:

  from es.EsClient import EsClient
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
class Hilst(Template, EsCommon):

  def __init__(self, deploy: str) -> None:
    global PROJ_ROOT_DIR 
    EsCommon.__init__(self)
    self._es_client: Elasticsearch = EsClient.get_es_client(deploy=deploy)

    self._flag: str = "hil"
    self._team_name: str = "현대건설배구단"
    self._base_url: str = "https://hillstate.hdec.kr"
    self._url_path: str = "/Contents_Player/Player"
    self._player_url_list: list[str] = list() 
    self._hillst_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"img/{self._flag}")
    self._char_delimiters = "년", "월", "일"
    self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

    self._position = {
      "LEFT": "OS"
      ,"RIGHT": "OP"
      ,"SETTER": "S"
      ,"CENTER": "C"
      ,"LIBERO": "L"
    }

  def get_url(self):
    '''
    '''
    response: requests.models.Response = requests.get(f"{self._base_url}{self._url_path}")
    #print(f"type: {type(response)}")

    if response.status_code == 200:
      bs_object = BeautifulSoup(response.text, "html.parser")
      player_list: bs4.element.Tag = bs_object.select_one("div.player-list")

      select_tag: str = \
                  "{tag}.{attri}"\
                  .format(tag="div", attri="swiper-container.swiper-squad-player") +\
                  " > " +\
                  "{tag}.{attri}"\
                  .format(tag="ul", attri="ls-squad-player.swiper-wrapper")
      #print(f"{select_tag}")
      li_tag_select: str = "{tag}.{attri}".format(tag="li", attri="swiper-slide")
      
      player_list: list = [p for p in player_list.select_one(select_tag).select(li_tag_select) if p]
      for p in player_list:
        p: bs4.element.Tag = p
        div_tag = p.select("div.li-inner")
 
        for d in div_tag:
          a_tag = d.select_one(
            "div.img-area" +\
            " > " +\
            "div.cover-wrap" +\
            " > " +\
            "a.btn-more.btn.white-bor-blue.mid")
          href_url:str = a_tag.attrs["href"]
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
              player_team_name= self._team_name,
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
          player_profile:bs4.element.Tag = bs_object.select_one("div.player-profile-wrap")
          top_area = player_profile.select_one(
            "div.top-area" +\
            " > " +\
            "div.thumb-swiper-wrap" +\
            " > " +\
            "div.player-info"
          )

          try:

            player_position = top_area.select_one(
              "div.position")
            player_position:str = str(player_position.text).strip()
            player_position:str = self._position[player_position]
            player_info["player_position"] += player_position
          except:
            pass 

          try:
            
            player_number = top_area.select_one(
              "div.number" +\
              " > " +\
              "span"              
            )
            player_number = int(str(player_number.text).strip().lstrip("0"))
            player_info["player_number"] += player_number
          except:
            pass
          
          try:
            
            player_name = top_area.select_one(
              "div.name"
            )
            player_name = str(player_name.text).strip()
            player_info["player_name"] += player_name
          except:
            pass

          
          player_detail_profile = player_profile.select_one(
            "div.bottom-area" +\
            " > " +\
            "div.profile-info" +\
            " > " +\
            "div.cont-area" +\
            " > " +\
            "ul"
          )

          li_tag_list = player_detail_profile.select("li.tpA")
          for l in li_tag_list:
            tit:str = str(l.select_one("p.tit").text)
            
            if tit == "생년월일":
              v:str = str(l.select_one("p.cont").text).replace(" ", "")
              player_birthday: list[str] = [e for e in re.split(self._regex_pattern, v) if e]
              player_info["player_birthday"]["year"] = int(player_birthday[0])
              player_info["player_birthday"]["month"] = int(str(player_birthday[1]).lstrip("0"))
              player_info["player_birthday"]["day"] = int(str(player_birthday[2]).lstrip("0"))
            
            elif tit == "신장/체중":
              v:list[str] = str(l.select_one("p.cont").text).replace(" ", "").split("/")
              v = float(str(v[0]).rstrip("cm"))
              player_info["player_height"] += v
            
            elif tit == "출신학교":
              v:list[str] = str(l.select_one("p.cont").text).replace(" ", "").split("-")
              if v:
                player_info["player_school"].extend(v)

          # ===================================================================================
          img_tag = player_profile.select_one(
            "div.player-img" +\
            " > " +\
            "img"
          )

          url_src_encoding:str = parse.quote(img_tag.attrs["src"])

          img_file_path:str = f"{self._hillst_photo_path}/{player_info['player_name']}.png"
          
          try:
            
            urllib.request.urlretrieve(
              self._base_url + url_src_encoding,
              img_file_path)
          except:
            print(f"img download fail")
            pass 
          else: 
            player_info["player_img_path"] += img_file_path
        
          print(player_info)
          self._es_action.append(
            {
              "_index": self._es_index
              , "_source": player_info
            })
        else:
          ''''''
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
  o = Hilst(deploy="local")
  o.get_url()
  o.player_detail_information()
  o.document_bulk_insert()

