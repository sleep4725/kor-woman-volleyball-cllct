from abc import *

class Template(metaclass= ABCMeta):

  @abstractmethod
  def get_url(self):
    pass 

  @abstractmethod
  def player_detail_information(self):
    pass