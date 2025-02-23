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
from game_records.models import UserTournamentGameRecord, TournamentMatch
from users.models import CustomUser


class TournamentGameGroup:
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

    def make_game_group_co_routine(self, width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius):
        if self.task == None:
            self.task = asyncio.create_task(self.run_game_group(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius))

    def send_message(self, direction, channel_name):
        self.game_manager.move_paddles(direction, channel_name)
    
    async def run_game_group(self, width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius):
        task = None
        channels = []

        winner_channels = []
        defeat_channels = []

        channels = self.channels[:2]
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        task = asyncio.create_task(self.run_game_loop())
        await task

        round_scores = self.games_scores[0]
        if round_scores[0] == 5:
            winner_channels.append(channels[0])
            defeat_channels.append(channels[1])
        elif round_scores[1] == 5:
            winner_channels.append(channels[1])
            defeat_channels.append(channels[0])

        channels = self.channels[2:]
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        task = asyncio.create_task(self.run_game_loop())
        await task
        
        round_scores = self.games_scores[1]
        if round_scores[0] == 5:
            winner_channels.append(channels[0])
            defeat_channels.append(channels[1])
        elif round_scores[1] == 5:
            winner_channels.append(channels[1])
            defeat_channels.append(channels[0])

        channels = winner_channels
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        task = asyncio.create_task(self.run_game_loop())
        await task

        channels = defeat_channels
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        task = asyncio.create_task(self.run_game_loop())
        await task
        
        logger.debug(self.games_scores)
        logger.debug(self.games_users)
        await self.store_game_result()

    async def send_game_state(self):
        game_state = self.game_manager.get_state()
        # 그룹 내 모든 클라이언트에게 게임 상태 전송
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send.game.state",
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
        while self.online_channels[self.game_manager.channels[0]] and self.online_channels[self.game_manager.channels[1]]:
            game = self.game_manager.run()  # 게임 상태 업데이트 (공, 패들 이동 등)

            match game:
                case GameState.RUNNING:
                    await self.send_game_state()
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
        await self.send_game_state()
        logger.debug("게임 끝")
        logger.debug(self.online_channels)
        logger.debug("게임 끝")
        if self.online_channels[self.game_manager.channels[0]] == False:
            await self.append_game_result([-1,5])
        elif self.online_channels[self.game_manager.channels[0]] == False:
            await self.append_game_result([5,-1])
        else:
            await self.append_game_result()
        return

    async def store_game_result(self):
        logger.debug("게임 기록 저장 시작.")
        round1_player1 = self.games_users[0][0]
        round1_player2 = self.games_users[0][1]
        round1_point1 = self.games_scores[0][0]
        round1_point2 = self.games_scores[0][1]
        round2_player1 = self.games_users[1][0]
        round2_player2 = self.games_users[1][1]
        round2_point1 = self.games_scores[1][0]
        round2_point2 = self.games_scores[1][1]
        round3_player1 = self.games_users[2][0]
        round3_player2 = self.games_users[2][1]
        round3_point1 = self.games_scores[2][0]
        round3_point2 = self.games_scores[2][1]
        round4_player1 = self.games_users[3][0]
        round4_player2 = self.games_users[3][1]
        round4_point1 = self.games_scores[3][0]
        round4_point2 = self.games_scores[3][1]

        match = await asyncio.to_thread(
            TournamentMatch.objects.create,
            round1_player1 = round1_player1,
            round1_player2 = round1_player2,
            round1_point1 = round1_point1,
            round1_point2 = round1_point2,
            round2_player1 = round2_player1,
            round2_player2 = round2_player2,
            round2_point1 = round2_point1,
            round2_point2 = round2_point2,
            round3_player1 = round3_player1,
            round3_player2 = round3_player2,
            round3_point1 = round3_point1,
            round3_point2 = round3_point2,
            round4_player1 = round4_player1,
            round4_player2 = round4_player2,
            round4_point1 = round4_point1,
            round4_point2 = round4_point2,
        )
        for channel in self.channels:
            await asyncio.to_thread(
                UserTournamentGameRecord.objects.create,
                user=self.users[channel],
                tournament_match_id=match
            )
        logger.debug("게임 기록 저장!")