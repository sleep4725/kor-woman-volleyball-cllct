import os
import sys 
PROJ_ROOT_PATH :str=os.path.dirname(os.path.abspath(os.path.dirname(__file__))) 
sys.path.append(PROJ_ROOT_PATH)

try:    
    from flask import Flask, render_template, request 
    from elasticsearch import Elasticsearch
except ImportError as error:
    print(error)

try:
    from es.EsClient import EsClient
    from es.EsQuery import EsQuery
    from common.EsIndex import EsIndex
except ImportError as error:
    print(error)
    
'''
@author JunHyeon.Kim
@date 20221210
'''
es_client :Elasticsearch = EsClient.get_es_client(deploy="local") 

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/es-cluster-health/<es_cluster>")
def get_es_cluster_health(es_cluster:str):
    '''
    :param esCluster:
    :return:
    '''
    global es_client
    if es_cluster not in ["local"]:
        return {"result": f"{es_cluster} is not exists cluster"}
    else:
        response :dict[str, object] = es_client.cluster.health()
        return render_template(
            "es-cluster.html", 
            es_cluster= es_cluster,
            response = response)    
    
@app.route("/sample")
def index():
    return render_template("sample.html")

@app.route("/player/<player_name>")
def get_player_detail_information(player_name):
    '''
    :param:
    :return:
    '''
    global es_client
    query :dict = EsQuery.get_player_detail_information(player_name=player_name)
    response :dict= es_client.search(body=query, index=EsIndex.KOR_WOM_INDEX)
    return render_template("player-img.html", player_name=player_name, hits_list=response["hits"])
     
if __name__ == "__main__":
    
    app.run(
        port=8055
        ,debug=True
    )