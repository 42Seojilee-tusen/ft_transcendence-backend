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
    def __init__(self, channels, user_ids):
        self.channel_layer = None
        # 게임을 진행시킬 게임 매니저
        self.game_manager = None
        # 1대1 게임 전체를 관리하는 코루틴
        self.task = None
        # 참가한 채널들 (2인)
        self.channels = channels
        # 참가한 채널에 대응하는 유저 객체 (2인)
        self.user_ids = {channel: user for channel, user in zip(self.channels, user_ids)}
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

    async def get_user_object(self, user_id):
        user: CustomUser = await asyncio.to_thread(
            lambda: CustomUser.objects.get(id=user_id)
        )
        return user

    async def get_user_datas(self, channels):
        res = []

        for channal in channels:
            user_id = self.user_ids[channal]
            user: CustomUser = await self.get_user_object(user_id)
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
        # 진행중인 게임 태스크
        task = None
        # 진행중인 채널들 -> 2명
        channels = []

        # 이긴 채널들 -> 3라운드 대상자
        winner_channels = []
        # 진 채널들 -> 4라운드 대상자
        defeat_channels = []

        # 게임 시작

        # 게임할 두명 선택
        channels = self.channels[:2]
        all_game_users = await self.get_user_datas(self.channels)
        now_game_users = await self.get_user_datas(channels)
        
        # 매챙된 4명의 유저 알림
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'matching.on',
                'game_users': all_game_users,
                'now_players': now_game_users,
            }
        )
        
        # 게임하는 유저들 알림
        await self.send_next_user(now_game_users)
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        await asyncio.sleep(3)
        task = asyncio.create_task(self.run_game_loop())
        await task

        round_scores = self.games_scores[0]
        if round_scores[0] == 5:
            winner_channels.append(channels[0])
            defeat_channels.append(channels[1])
        elif round_scores[1] == 5:
            winner_channels.append(channels[1])
            defeat_channels.append(channels[0])
            
        await self.send_finish(round_scores)

        await asyncio.sleep(3)

        channels = self.channels[2:]
        
        
        now_game_users = await self.get_user_datas(channels)
        await self.send_next_user(now_game_users)
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        await asyncio.sleep(3)
        task = asyncio.create_task(self.run_game_loop())
        await task
        
        round_scores = self.games_scores[1]
        if round_scores[0] == 5:
            winner_channels.append(channels[0])
            defeat_channels.append(channels[1])
        elif round_scores[1] == 5:
            winner_channels.append(channels[1])
            defeat_channels.append(channels[0])
        await self.send_finish(round_scores)
        await asyncio.sleep(3)

        channels = winner_channels
        now_game_users = await self.get_user_datas(channels)
        await self.send_next_user(now_game_users)
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        await asyncio.sleep(3)
        task = asyncio.create_task(self.run_game_loop())
        await task

        round_scores = self.games_scores[2]
        await self.send_finish(round_scores)
        await asyncio.sleep(3)
        
        
        channels = defeat_channels
        now_game_users = await self.get_user_datas(channels)
        await self.send_next_user(now_game_users)
        self.game_manager = GameManager(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius, channels, ball_count=1)
        await asyncio.sleep(3)
        task = asyncio.create_task(self.run_game_loop())
        await task
        
        round_scores = self.games_scores[3]
        await self.send_finish(round_scores)
        await asyncio.sleep(3)
        
        if self.games_scores[2][0] == 5:
            winner_channel = [winner_channels[0]]
        elif self.games_scores[2][1] == 5:
            winner_channel = [winner_channels[1]]
        
        winner_user = await self.get_user_datas(winner_channel)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'game.end',
                'winner': winner_user
            }
        )
        await self.store_game_result()

    async def send_next_user(self, users):
        now_players = users
        # now_players = [user['player_name'] for user in users]
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'next.game',
                'now_players': now_players,
            }
        )

    async def send_finish(self, round_scores):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'finish',
                'result': round_scores
            }
        )

    async def send_game_state(self, channels):
        game_state = self.game_manager.get_state()
        
        game_users = await self.get_user_datas(channels)
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
            games_user.append(self.user_ids[channel])
        self.games_users.append(games_user)

    async def send_wait_state(self, time):
        for i in range(time, 0, -1):
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send.wait",
                    "time": i,
                    "scores": self.game_manager.get_scores()
                }
            )
            await asyncio.sleep(1)

    async def run_game_loop(self):
        """게임 루프 실행 (60FPS)"""
        channels = self.game_manager.channels
        await self.send_game_state(channels)
        await self.send_wait_state(3)
        while self.online_channels[channels[0]] and self.online_channels[channels[1]]:
            game = self.game_manager.run()  # 게임 상태 업데이트 (공, 패들 이동 등)

            match game:
                case GameState.RUNNING:
                    await self.send_game_state(channels)
                case GameState.POINT_SCORED:
                    await self.send_wait_state(3)
                case GameState.GAME_OVER:
                    break
            # 현재 게임 상태 가져오기
            await asyncio.sleep(1 / 60)  # 60FPS (0.016초 대기)
        logger.debug("게임 끝")
        logger.debug(self.online_channels)
        logger.debug("게임 끝")
        if self.online_channels[channels[0]] == False:
            await self.append_game_result([-1,5])
        elif self.online_channels[channels[1]] == False:
            await self.append_game_result([5,-1])
        else:
            await self.append_game_result()
        return

    async def store_game_result(self):
        logger.debug("게임 기록 저장 시작.")
        round1_player1 = await self.get_user_object(self.games_users[0][0])
        round1_player2 = await self.get_user_object(self.games_users[0][1])
        round1_point1 = self.games_scores[0][0]
        round1_point2 = self.games_scores[0][1]
        round2_player1 = await self.get_user_object(self.games_users[1][0])
        round2_player2 = await self.get_user_object(self.games_users[1][1])
        round2_point1 = self.games_scores[1][0]
        round2_point2 = self.games_scores[1][1]
        round3_player1 = await self.get_user_object(self.games_users[2][0])
        round3_player2 = await self.get_user_object(self.games_users[2][1])
        round3_point1 = self.games_scores[2][0]
        round3_point2 = self.games_scores[2][1]
        round4_player1 = await self.get_user_object(self.games_users[3][0])
        round4_player2 = await self.get_user_object(self.games_users[3][1])
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
            user:CustomUser = await self.get_user_object(self.user_ids[channel])
            await asyncio.to_thread(
                UserTournamentGameRecord.objects.create,
                user=user,
                tournament_match_id=match
            )
        logger.debug("게임 기록 저장!")