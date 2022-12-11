'''
@author JunHyeon.Kim
@date 20221210
'''
class EsQuery:
    
    @classmethod 
    def get_player_detail_information(cls, player_name: str)\
        -> dict:
        '''
        :param player_name:
        '''
        return {
            "query": {
                "term": {
                    "player_name": {
                        "value": f"{player_name}"
                    }   
                }
            }
        }