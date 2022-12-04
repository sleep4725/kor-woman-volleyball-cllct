from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

"""
@author JunHyeon.Kim
"""
class EsCommon:

  def __init__(self) -> None:
    self._es_index:str = "woman_volley_ball"
    self._es_action:list = list()

  def bulk_insert(self, es_client: Elasticsearch):
    '''
    :param: es_client
    '''
    if len(self._es_action) > 0:
      try:

        bulk(es_client, self._es_action)
      except:
        print("bulk insert fail")
    else:
      print("bulk insert fail")
