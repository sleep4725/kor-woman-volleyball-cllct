from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch

"""
@author JunHyeon.Kim
"""
class EsCommon:

  def __init__(self) -> None:
    self._es_action:list = list()

  def bulk_insert(self, es_client: Elasticsearch):
    '''
    :param: es_client
    '''
    try:

      bulk(client= es_client, actions= self._es_action)
    except:
      print("bulk insert fail")
    else:
      print("bulk insert success")

