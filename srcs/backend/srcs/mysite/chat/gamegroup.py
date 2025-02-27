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
from chat.gamemanager import GameManager, GameState
import uuid
import logging
logger = logging.getLogger('chat') 
from game_records.models import UserOneOnOneGameRecord, OneOnOneMatch
from users.models import CustomUser


class GameGroup:
    def __init__(self, channels, users):
        self.channel_layer = None
        # 게임을 진행시킬 게임 매니저
        self.game_manager = None
        # 1대1 게임 전체를 관리하는 코루틴
        self.task = None
        # 참가한 채널들 (2인)
        self.channels = channels
        # 참가한 채널에 대응하는 유저 객체 (2인)
        self.users = {channel: user for channel, user in zip(self.channels, users)}
        # 참가한 채널이 접속중인지 확인하는 딕셔너리
        self.online_channels = {channel: True for channel in self.channels}
        self.user_count = len(self.channels)
        self.group_name = f"{uuid.uuid4().hex}"

        # [5, 3] 형태로 진행된 게임 순서대로 스코어 저장
        # 유저도 마찬가지
        self.games_scores = []
        self.games_users = []

    async def disconnect_channel(self, channel):
        self.user_count -= 1
        self.online_channels[channel] = False
    
    def get_user_datas(self, channels):
        res = []

        for channal in channels:
            user = self.users[channal]
            res.append({
                'player_name': user.username,
                'player_image': user.profile_image.url
            })
        return res

    def make_game_group_co_routine(self, width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius):
        if self.task == None:
            self.task = asyncio.create_task(self.run_game_group(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius))

    def send_message(self, direction, channel_name):
        self.game_manager.move_paddles(direction, channel_name)

    async def run_game_group(self, width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius):
        task = None
        channels = self.channels
        

        game_users = self.get_user_datas(channels)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'matching.on',
                'game_users': game_users
            }
        )
        await asyncio.sleep(3)

        # await self.send(text_data=text_data)

        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        task = asyncio.create_task(self.run_game_loop())
        
        await task
        
        game_users = self.get_user_datas(channels)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'game.end',
                'now_players': game_users,
                'result': self.games_scores[0]
            }
        )
        await asyncio.sleep(3)
        
        logger.debug(self.games_scores)
        logger.debug(self.games_users)
        await self.store_game_result()


    async def send_game_state(self, channels):
        game_state = self.game_manager.get_state()
        
        game_users = self.get_user_datas(channels)
        # 그룹 내 모든 클라이언트에게 게임 상태 전송
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send.game.state",
                "now_players": game_users,
                "game_state": game_state,
            }
        )

    async def append_game_result(self, scores=None):
        game_state = self.game_manager.get_state()
        if scores == None:
            self.games_scores.append(game_state['scores'])
        else:
            self.games_scores.append(scores)
        games_user = []
        for channel in self.game_manager.channels:
            games_user.append(self.users[channel])
            self.games_users.append(games_user)

    async def run_game_loop(self):
        """게임 루프 실행 (60FPS)"""
        channels = self.game_manager.channels
        while self.online_channels[channels[0]] and self.online_channels[channels[1]]:
            game = self.game_manager.run()  # 게임 상태 업데이트 (공, 패들 이동 등)

            match game:
                case GameState.RUNNING:
                    await self.send_game_state(channels)
                case GameState.POINT_SCORED:
                    for i in range(3, 0, -1):
                        await self.channel_layer.group_send(
                            self.group_name,
                            {
                                "type": "send.wait",
                                "time": i
                            }
                        )
                        await asyncio.sleep(1)
                case GameState.GAME_OVER:
                    break
            # 현재 게임 상태 가져오기
            await asyncio.sleep(1 / 60)  # 60FPS (0.016초 대기)
        await self.send_game_state(channels)
        logger.debug("게임 끝")
        logger.debug(self.online_channels)
        logger.debug("게임 끝")
        if self.online_channels[channels[0]] == False:
            await self.append_game_result([-1,5])
        elif self.online_channels[channels[0]] == False:
            await self.append_game_result([5,-1])
        else:
            await self.append_game_result()
        return

    async def store_game_result(self):
        logger.debug("게임 기록 저장 시작.")
        player1 = self.games_users[0][0]
        player2 = self.games_users[0][1]
        point1 = self.games_scores[0][0]
        point2 = self.games_scores[0][1]
        
        match = await asyncio.to_thread(
            OneOnOneMatch.objects.create,
            player1=player1,
            player2=player2,
            point1=point1,
            point2=point2
        )
        for channel in self.channels:
            await asyncio.to_thread(
                UserOneOnOneGameRecord.objects.create,
                user=self.users[channel],
                one_on_one_match_id=match
            )
        logger.debug("게임 기록 저장!")
    