"""GameGroup
게임 그룹을 관리하는 클래스

역할
1. GameManager 객체 보유
2. 코루틴 task 보유
3. 유저 구분 정보 보유
6. 그룹의 참가중인 유저 수 보유
4. 매치 메이커에서 반환해주는 객체
5. 게임 만들기를 통해 코루틴과 게임 객체를 생성
"""
import asyncio
from chat.gamemanager import GameManager
import uuid

class TournamentGameGroup:
    def __init__(self, channels, users):
        self.game_manager = None
        self.task = None
        self.channels = channels
        self.users = users
        self.user_count = len(self.channels)
        self.group_name = f"{uuid.uuid4().hex}"

    def make_game(self, run_game_loop, width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius):
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, self.channels, ball_count=1)
        self.task = asyncio.create_task(run_game_loop(self.game_manager, self))
    
    def send_message(self, direction, channel_name):
        self.game_manager.move_paddles(direction, channel_name)