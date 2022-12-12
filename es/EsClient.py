import os
import sys
PROJ_ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

import yaml
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
## ----------------------
# @author JunHyeon.Kim
# @date 20221010
## ----------------------
class EsClient:

    @classmethod
    def get_es_client(cls, deploy: str)-> Elasticsearch:
        '''
        :param deploy:
        :return Elasticsearch-client:
        '''
        ES_DEPLOY_LIST: list[str] = ["local"]
        global PROJ_ROOT_DIR

        ES_CONN_INFO :str= os.path.join(PROJ_ROOT_DIR, "config/es-conn.yaml")
        is_file_exists = os.path.exists(ES_CONN_INFO)

        if is_file_exists:
            with open(ES_CONN_INFO, "r", encoding="utf-8") as es_conn:
                es_conn_yaml :dict= yaml.safe_load(es_conn)
                es_conn.close()

                if deploy in ES_DEPLOY_LIST:
                    es_conn_config = es_conn_yaml[deploy]
                    _port: int = es_conn_config["port"]
                    _schema: str = es_conn_config["schema"]
                    _es_client: Elasticsearch = Elasticsearch([
                        f"{_schema}://{h}:{_port}" for h in es_conn_config["hosts"]
                    ])
                    try:
                        
                        response = _es_client.cluster.health()
                    except ConnectionError as error:
                        print(error)
                        exit(1)
                    else:
                        print(f"************ {response}")
                        return _es_client
                else:
                    return None
        else:
            raise FileNotFoundError