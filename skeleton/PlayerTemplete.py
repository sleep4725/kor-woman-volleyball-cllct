from dataclasses import dataclass, asdict

@dataclass
class PlayerTemplate:
  player_name: str 
  player_number: int
  player_position: str
  player_detail_url: str
  player_height: float
  player_birthday: dict
  player_school: list 
  player_img_path: str
  player_team_name: str