import re
import os
import sys
PROJ_ROOT_DIR= os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(PROJ_ROOT_DIR)

import requests
import urllib.request
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import bs4
from dataclasses import asdict

try:
    from es.EsClient import EsClient
    from common.EsCommon import EsCommon
    from skeleton.Template import Template
    from skeleton.PlayerTemplete import PlayerTemplate
except ImportError as err:
  print(err)
  exit(1)

"""
kgc 인삼공사 프로 배구단 
@author JunHyeon.Kim
@date 20221204
"""
class Kgc(Template, EsCommon):

    def __init__(self, deploy: str)-> None:
        '''
        :param deploy:
        '''
        global PROJ_ROOT_DIR
        EsCommon.__init__(self)
        self._es_client:Elasticsearch= EsClient.get_es_client(deploy=deploy)

        self._flag: str = "kgc"
        self._team_name: str = "kgc인삼공사"
        self._base_url: str = "https://www.kgcsports.com"
        self._url_path: str = "/volleyball/player"
        self._url_path_bottom: str = "/player_list.php"
        self._player_url_list: list[str] = list()
        self._char_delimiters = "년", "월", "일"
        self._regex_pattern = "|".join(map(re.escape, self._char_delimiters))
        self._kgc_photo_path: str = os.path.join(PROJ_ROOT_DIR, f"img/{self._flag}")

        self._position = {
            "아포짓(스파이커)": "OP"
            ,"아웃사이드 히터": "OS"
            ,"미들 블로커": "MB"
            ,"세터": "S"
            ,"리베로": "L"
        }

    def get_url(self):
        """
        :param:
        :return:
        """
        response: requests.models.Response = requests.get(
            self._base_url +
            self._url_path +
            self._url_path_bottom
        )
        if response.status_code == 200:
            bs_object: bs4.element.Tag = BeautifulSoup(response.text, "html.parser")
            content_tag: bs4.element.Tag = bs_object.select_one("div#contents")
            p_list_tag: bs4.element.ResultSet = content_tag.select("div.plist")

            for p_tag in p_list_tag:
                p_tag :bs4.element.Tag = p_tag
                a_tag:bs4.element.Tag = p_tag.select_one("dl > dd > ul")
                li_tags:bs4.element.ResultSet = a_tag.select("li")

                for l in li_tags:
                    l: bs4.element.Tag = l
                    a_tag: bs4.element.Tag = l.select_one("a")
                    href_url: str = str(a_tag.attrs["href"])
                    self._player_url_list.append(
                        self._base_url + f"{self._url_path}/{href_url}"
                    )
        else:
            ''''''

        response.close()

    def get_player_position(self, l: bs4.element.Tag, result: str)\
            -> str:
        '''
        선수 포지션
        :param l:
        :param result:
        :return:
        '''

        return self._position[str(l.text).lstrip(result)]

    def get_player_number(self, l:bs4.element.Tag, result: str)\
            -> int:
        '''
        선수 백넘버
        :param l:
        :param result:
        :return:
        '''
        return int(str(l.text).lstrip(result).lstrip("0"))

    def get_player_birthday(self, l:bs4.element.Tag, result: str)\
            -> list[int]:
        '''
        :param l:
        :param result:
        :return:
        '''
        return [int(str(p_bir).lstrip("0")) for p_bir in str(l.text).lstrip(result).split(".")]

    def get_player_school(self, l:bs4.element.Tag, result: str)\
            -> list[str]:
        '''
        :param l:
        :param result:
        :return:
        '''
        return [str(p_sch).strip() for p_sch in str(l.text).lstrip(result).split("-")]

    def get_player_height(self, l:bs4.element.Tag, result: str)\
            -> float:
        '''
        :param l:
        :param result:
        :return:
        '''
        return float(str(l.text).lstrip(result).
                                 rstrip("\n").
                                 rstrip().
                                 rstrip("cm"))

    def download_player_img(self,
                            img_file_path: str,
                            player_profile_tag: bs4.element.Tag)\
            ->None:
        '''
        :param img_file_path:
        :param player_profile_tag:
        :return None:
        '''


        player_img_tag: bs4.element.Tag = player_profile_tag.select_one("img")
        player_img_url: str = self._base_url + player_img_tag.attrs["src"]

        try:

            urllib.request.urlretrieve(player_img_url, img_file_path)
        except:
            print(f"img download fail")
            pass

    def player_detail_information(self):
        '''

        '''
        if len(self._player_url_list) > 0:
            for u in self._player_url_list:
                player_info = asdict(
                    PlayerTemplate(
                        player_name="",
                        player_team_name=self._team_name,
                        player_number=0,
                        player_position="",
                        player_detail_url="",
                        player_height=.0,
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
                # ------------------------------------------------------
                response: requests.models.Response = requests.get(u)

                if response.status_code == 200:
                    bs_object:bs4.element.Tag = BeautifulSoup(response.text, "html.parser")
                    player_profile_tag:bs4.element.Tag = bs_object.select_one("div.player_profile")

                    player_p_namebox:bs4.element.Tag = bs_object.select_one("div.p_namebox > h4.player_tt > strong")
                    player_name:str = str(player_p_namebox.text).strip()
                    player_info["player_name"] += player_name
                    img_file_path: str = f"{self._kgc_photo_path}/{player_name}.png"

                    self.download_player_img(img_file_path=img_file_path,
                                             player_profile_tag= player_profile_tag)

                    player_detail_tag:bs4.element.Tag = player_profile_tag.select_one("ul.player_detail")
                    li_tags:bs4.element.ResultSet = player_detail_tag.select("li")
                    player_info["player_img_path"] += img_file_path

                    for l in li_tags:
                        l:bs4.element.Tag = l
                        result:str = str(l.select_one("em").text)

                        if result == "포지션":
                            player_info["player_position"] += self.get_player_position(l=l, result=result)

                        elif result == "배번":
                            player_info["player_number"] += self.get_player_number(l=l, result=result)

                        elif result == "생년월일":
                            player_birthday_list: list[int] = self.get_player_birthday(l=l, result=result)
                            player_info["player_birthday"]["year"] = player_birthday_list[0]
                            player_info["player_birthday"]["month"] = player_birthday_list[1]
                            player_info["player_birthday"]["day"] = player_birthday_list[2]

                        elif result == "출신학교":
                            player_info["player_school"].extend(self.get_player_school(l=l, result=result))

                        elif result == "신장":
                            player_info["player_height"] += self.get_player_height(l=l, result=result)

                    print(player_info)
                    self._es_action.append(
                        {
                            "_index": self._es_index
                            ,"_source": player_info
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
    o = Kgc(deploy="local")
    o.get_url()
    o.player_detail_information()
    o.document_bulk_insert()