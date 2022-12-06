import re 
import os 
import sys 
PROJ_ROOT_DIR= os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PROJ_ROOT_DIR)

import requests 
import urllib.request
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
class AIPepp(Template, EsCommon):
  ''''''
  def __init__(self, deploy: str) -> None:
    global PROJ_ROOT_DIR 
    EsCommon.__init__(self)
    self._es_client: Elasticsearch = EsClient.get_es_client(deploy=deploy)

    self._char_delimiters = "년", "월", "일"
    self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

    self._flag: str = "aip"
    self._team_name: str = "에이아이페퍼스"
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
      bs_object:bs4.element.Tag = BeautifulSoup(response.text, "html.parser")
      team_sub_list:bs4.element.Tag = bs_object.select_one(
        "div#team_sub1_section2" +
        " > " +
        "ul"
      )

      li_tags:bs4.element.ResultSet = team_sub_list.select("li")

      for l in li_tags:
        l:bs4.element.Tag = l
        a_tag:bs4.element.Tag = l.select_one(
              "div.player_thmbs" +
              " > " +
              "a"
        )

        href_url: str = a_tag.attrs["href"]
        self._player_url_list.append(self._base_url + "/" + href_url)
    else:
      ''''''

  def get_player_position(self, player_detail_info: bs4.element.Tag)\
          -> str:
      '''
      선수 포지션
      :param player_detail_info:
      :return:
      '''
      player_position: str = str(player_detail_info.select_one("h3").text).strip()
      return player_position

  def get_player_number(self, player_detail_info: bs4.element.Tag)\
          -> int:
      '''
      선수 백넘버
      :return:
      '''
      player_number: int = int(str(player_detail_info.select_one("h2").text).lstrip("No.").lstrip("0").strip())
      return player_number

  def get_player_name(self, player_detail_info: bs4.element.Tag)\
          -> str:
      '''
      선수 이름
      :return:
      '''
      player_name_tag: bs4.element.Tag = player_detail_info.select_one(
        "p" +
        " > " +
        "span"
      )
      player_name: str = str(player_name_tag.text).strip()
      return player_name

  def get_player_birthday(self, birthday: str)\
          -> list[int]:
      '''
      선수 생일
      :return:
      '''

      return [int(str(b).lstrip("0").strip()) for b in birthday.split(".")]

  def get_player_school(self, school: str)\
          -> list[str]:
      '''
      :param l:
      :param result:
      :return:
      '''
      return [str(s).strip() for s in school.split("/")]

  def get_player_height(self, height: str) \
          -> float:
    '''
    :param:
    :return:
    '''
    return float(height.rstrip("cm"))

  def download_player_img(self,
                          img_file_path: str,
                          player_detail_info: bs4.element.Tag) \
          -> None:
    '''
    :param img_file_path:
    :param player_detail_info:
    :return None:
    '''

    player_img_tag: bs4.element.Tag = player_detail_info.select_one(
      "div.player_detail_btn" +
      " > " +
      "a"
    )
    player_req_url: str = player_img_tag.attrs["href"]
    response: requests.models.Response = requests.get(player_req_url)
    if response.status_code == 200:
      bs_object : bs4.element.Tag = BeautifulSoup(response.text, "html.parser")
      img_tag: bs4.element.Tag = bs_object.select_one(
        "div.player_profile.box" +
        " > " +
        "div.clearfix" +
        " > " +
        "div.img" +
        " > " +
        "img"
      )

      player_img_url: str = "https://www.kovo.co.kr" + img_tag.attrs["src"]
      try:

        urllib.request.urlretrieve(player_img_url, img_file_path)
      except:
        print(f"img download fail")
        pass
    else:
      ''''''

  def player_detail_information(self):
    '''

    '''
    if len(self._player_url_list) > 0:
      for u in self._player_url_list:
        player_info = asdict(
          PlayerTemplate(
            player_name="",
            player_team_name= self._team_name,
            player_number=0,
            player_position="",
            player_detail_url="",
            player_height=0,
            player_birthday={
              "year": None
              , "month": None
              , "day": None
            },
            player_school=[],
            player_img_path=""
          )
        )
        player_info["player_detail_url"] = u
        response: requests.models.Response = requests.get(u)

        if response.status_code == 200:
          bs_object: bs4.element.Tag = BeautifulSoup(response.text, "html.parser")
          team_sub1_section2: bs4.element.Tag = bs_object.select_one("div#team_sub1_section2")
          # img-download
          player_detail_tag: bs4.element.Tag = team_sub1_section2.select_one("div.player_detail")
          player_detail_info: bs4.element.Tag = player_detail_tag.select_one("div.player_detail_info")
          # 선수 포지션
          player_info["player_position"] += self.get_player_position(player_detail_info= player_detail_info)
          # 선수 백넘버
          player_info["player_number"] += self.get_player_number(player_detail_info= player_detail_info)
          # 선수 이름
          player_info["player_name"] += self.get_player_name(player_detail_info= player_detail_info)

          img_file_path: str = f"{self._aipepp_photo_path}/{player_info['player_name']}.png"
          self.download_player_img(img_file_path=img_file_path, player_detail_info= player_detail_info)
          player_info["player_img_path"] += img_file_path

          player_detail_info_tag : bs4.element.ResultSet = player_detail_info.select("span")
          for p in player_detail_info_tag[1:]:
            p: bs4.element.Tag = p
            player_detail_list: list[str] = [str(p) for p in str(p.text).replace(" ", "").strip().split("\n") if p]

            for element in player_detail_list:
              k, v = str(element).split(":")

              if k == "생년월일":
                birthday_list: list[int] = self.get_player_birthday(birthday=v)
                player_info["player_birthday"]["year"] = birthday_list[0]
                player_info["player_birthday"]["month"] = birthday_list[1]
                player_info["player_birthday"]["day"] = birthday_list[2]
              elif k == "출신학교":
                school_list: list[str] = self.get_player_school(school=v)
                player_info["player_school"].extend(school_list)
              elif k == "신장":
                player_height: float = self.get_player_height(height=v)
                player_info["player_height"] += player_height

          print(player_info)
          self._es_action.append(
            {
              "_index": self._es_index
              , "_source": player_info
            }
          )
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
  o = AIPepp(deploy="local")
  o.get_url()
  o.player_detail_information()
  o.document_bulk_insert()