import os
PROJ_ROOT_PATH= os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
import yaml 
from elasticsearch import Elasticsearch 

class EsClient:
  
  @classmethod 
  def get_es_client(cls):
    ''''''
    