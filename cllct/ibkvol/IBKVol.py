import re 
import os 
import sys 
PROJ_ROOT_DIR= os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PROJ_ROOT_DIR)

import requests 
import urllib.request
from bs4 import BeautifulSoup
from dataclasses import asdict
try:

  from common.EsCommon import EsCommon
  from skeleton.Template import Template
  from skeleton.PlayerTemplete import PlayerTemplate
except ImportError as err:
  print(err)
  exit(1)

"""
@author JunHyeon.Kim
@date 20221121
"""
class IBKVol(Template, EsCommon):

  def __init__(self) -> None:
    global PROJ_ROOT_DIR
    EsCommon.__init__(self)

    self._flag: str = "ibk"
    self._base_url: str = "http://sports.ibk.co.kr/m/volleyball/team/"
    self._base_url_path: str = "player.php"
    self._player_url_list: list[str] = list() 
    self._ibk_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"img/{self._flag}")
    self._char_delimiters = "년", "월", "일"
    self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))

  def get_url(self):
    '''
    :param:
    :return:
    '''
    response = requests.get(f"{self._base_url}{self._base_url_path}")
    
    if response.status_code == 200:
      bs_object = BeautifulSoup(response.text, "html.parser")
      li_tag_list: list = bs_object.select_one("ul.list_player").select("li") 

      for li_tag in li_tag_list:
        try:
          
          a_tag = li_tag.select_one("a.link_detail")
          wrap_desc = a_tag.select_one("div.wrap_desc")
          info_posi = wrap_desc.select_one("div.info_position")
            
          player_name= wrap_desc.select_one("strong.txt_name").text
          player_number= int(info_posi.select_one("span.num").text)
          player_position= info_posi.select_one("span.position").text
          player_detail_url= self._base_url + str(a_tag.attrs["href"]).lstrip("./")
            
          player_info = asdict(
            PlayerTemplate(
              player_name= player_name, 
              player_number= player_number,
              player_position= player_position,
              player_detail_url= player_detail_url,
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
          self._player_url_list.append(player_info)
        except:
          print("parsing error")
          pass 

    else:
      print("request error")

    response.close()
  
  def player_detail_information(self):
    '''
    :param:
    :return:
    '''
    if self._player_url_list:
      for u in self._player_url_list:
        
        response= requests.get(u['player_detail_url'])
        if response.status_code == 200:
          bs_object= BeautifulSoup(response.text, "html.parser")
          
          img_tag = bs_object.select_one("sapn.frame_g > img")
          
          img_file_path:str = f"{self._ibk_photo_path}/{u['player_name']}.jpg"
          
          try:
            
            urllib.request.urlretrieve(
              img_tag.attrs["src"], 
              img_file_path)
          except:
            pass 
          else: 
            u["player_img_path"] += img_file_path

          li_tag_list= bs_object.select_one("ul.list_profile").select("li")

          for l in li_tag_list:
            k, v = str(l.text).split(":")
            k = str(k).strip()
            
            if k == "생년월일":
              v = str(v).replace(" ", "")
              player_birthday: list[str] = [e for e in re.split(self._regex_pattern, v) if e]
              
              u["player_birthday"]["year"] = int(player_birthday[0])
              u["player_birthday"]["month"] = int(str(player_birthday[1]).lstrip("0"))
              u["player_birthday"]["day"] = int(str(player_birthday[2]).lstrip("0"))

            elif k == "출신학교":
              v = str(v).replace(" ", "")
              player_school:list[str] = [sch for sch in v.split("-") if sch]
              u["player_school"].extend(player_school)
            
            elif k == "신장":
              v = int(str(v).replace(" ", "").rstrip("cm"))
              u["player_height"] += v

          self._es_action.append(
            {
              "_index": self._es_index
              ,"_source": u
            }
          )
          print(u)
    else:
      print("empty list")

if __name__ == "__main__":
  o = IBKVol()
  o.get_url()
  o.player_detail_information()
