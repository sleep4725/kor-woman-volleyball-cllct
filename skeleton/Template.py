from abc import *

class Template(metaclass= ABCMeta):

  def __init__(self):
    pass

  @abstractmethod
  def get_url(self):
    pass 

  @abstractmethod
  def player_detail_information(self):
    pass

  @abstractmethod
  def get_player_position(self, *Object):
    """
    선수의 포지션 정보를 얻는다.
    """
    pass

  @abstractmethod
  def get_player_name(self, *Object):
    '''
    선수의 이름 정보를 얻는다.
    '''
    pass

  @abstractmethod
  def get_player_number(self, *Object):
    """
    선수의 등번호를 얻는다.
    """
    pass

  @abstractmethod
  def get_player_birthday(self, *Object):
    """
    선수의 생일 정보를 얻는다.
    """
    pass

  @abstractmethod
  def get_player_school(self, *Object):
    """
    선수의 학교 정보를 얻는다.
    """
    pass

  @abstractmethod
  def get_player_height(self, *Object):
    """
    선수의 키 정보를 얻는다.
    """
    pass

  @abstractmethod
  def download_player_img(self, *Object):
    """
    선수의 사진을 다운로드
    """
    pass
