# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from chat.matchmanager import MatchManager
from chat.gamemanager import GameState

import asyncio

import logging
logger = logging.getLogger('chat') 

class GameTournamentConsumer(AsyncWebsocketConsumer):
    # 접속한 클라이언트 수
    # id: 수
    active_channels = {}

    # 게임 대기중인 유저
    # 채널이름, 유저 객체
    match_manager = MatchManager()
    
    # 그룹 매니저
    # 그룹 이름으로 구분
    # GameGroup 객체가 저장됨
    game_groups = {}
    
    async def connect(self):
        self.user = self.scope["user"]
        # 게임 참가를 위한 그룹이름
        self.group_name = None
        try:
            # 유저 객체가 없거나, JWT토큰 인증이 안된 클라이언트 라면 에러를 던짐.
            if self.user is None or isinstance(self.user, AnonymousUser):
                logger.error("User not authenticated")
                raise Exception('User not authenticated')
            self.id = self.user.id
            # 유저의 수를 증가
            self.active_channels[self.id] = self.active_channels.get(self.id, 0) + 1
            
            # 내이름을 가진 유저의 수가 1명 이상이면 에러를 던짐 => 멀티 클라이언트
            if self.id in self.active_channels and self.active_channels[self.id] > 1:
                logger.error(f"{self.user.username} is multi client error")
                raise Exception('multi client error')
            
            # 웹소켓 접속을 수락
            await self.accept()
            
            # 매칭이 되면 GameGroup 반환
            game_group = self.match_manager.matching4(self.channel_name, self.id)
            
            # 매칭이되면 웹소켓 그룹 생성
            if game_group is not None:
                game_group.channel_layer = self.channel_layer
                self.group_name = game_group.group_name
                self.game_groups[self.group_name] = game_group
                for channel_name in self.game_groups[self.group_name].channels:
                    await self.channel_layer.group_add(self.group_name, channel_name)
                await self.channel_layer.group_send(
                    self.group_name, {'type':'matching.init', "group_name": self.group_name}
                )

        except Exception as e:
            logger.error(str(e))
            await self.close(code=4001)
            return 

    async def disconnect(self, close_code):
        # JWT토큰 인증 오류 유저
        if self.user is None or isinstance(self.user, AnonymousUser):
            logger.error("JWT인증이 안된 유저입니다.")
            return

        # 유저수를 1 감소
        # 만약 내가 마지막 유저였다면 해당 세트를 삭제
        self.active_channels[self.id] -= 1
        if self.active_channels[self.id] <= 0:
            self.active_channels.pop(self.id, None)
        else:
            return

        # 대기중인 유저 목록에서 자기자신 제거
        self.match_manager.del_waiting(self.channel_name)

        # 참가한 그룹이름이 존재한다면
        # if self.group_name:
        try:
            # 매칭되어있던 유저들에게 접속을 종료했음을 알림
            # 그룹에서 자기자신 삭제 후, 그룹 인원 수를 줄임.
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.game_groups[self.group_name].disconnect_channel(self.channel_name)
            # 아무도 남지 않았다면 실행중인 게임그룹 삭제
            if self.game_groups[self.group_name].user_count <= 0:
                # 셋에서 게임 그룹 삭제
                game_group = self.game_groups.pop(self.group_name, None)
                try:
                    task = game_group.task
                    if task:
                        task.cancel()  # 태스크 취소
                        try:
                            await task  # 태스크가 종료될 때까지 대기
                        except asyncio.CancelledError:
                            logger.debug(f"Game loop for {self.group_name} cancelled.")
                    logger.debug(f"GameManager for {self.group_name} deleted.")
                except Exception as e:
                    logger.debug("game task cancel error: " + str(e))
            # 자신의 그룹 이름을 None으로 설정
            self.group_name = None
        except Exception as e:
            logger.debug("group discard error: " + str(e))

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        if not data.get('type'):
            logger.debug("type is not define")
            return
        match data['type']:
            # 게임 초기화
            # 매칭 후 게임화면 준비를 할 수 있도록 메시지 전송?
            # case "game_init":
            #     if self.game_groups[self.group_name].game_manager:
            #         return
            #     width = data['width']
            #     height = data['height']
            #     paddle_speed = data['paddle_speed']
            #     paddle_xsize = data['paddle_xsize']
            #     paddle_ysize = data['paddle_ysize']
            #     ball_speed = data['ball_speed']
            #     ball_radius = data['ball_radius']
            #     game_group = self.game_groups.get(self.group_name, None)
            #     game_group.make_game_group_co_routine(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius)
            case "move_paddle":
                if self.group_name is None:
                    return
                
                direction = data['direction']
                game_group = self.game_groups.get(self.group_name, None)
                game_group.send_message(direction, self.channel_name)

    async def send_wait(self, event):
        """5초 기다리라는 표시"""
        text_data = json.dumps({
            'type': 'game_wait',
            'time': event['time'],
            'scores': event['scores'],
        })
        await self.send(text_data=text_data)

    async def send_game_state(self, event):
        """게임 상태를 웹소켓으로 클라이언트에 전송"""
        text_data = json.dumps({
            'type': 'game_update', 
            'now_players': event['now_players'],
            'game_state': event["game_state"]
        })
        # text_data = json.dumps(event["paddles"])
        await self.send(text_data=text_data)
    async def matching_init(self, event):
        logger.debug("matching_init")
        self.group_name = event['group_name']

        width = 800
        height = 500
        paddle_speed = 10
        paddle_xsize = 10
        paddle_ysize = 100
        ball_speed = 10
        ball_radius = 10
        game_group = self.game_groups.get(self.group_name, None)
        game_group.make_game_group_co_routine(width, height, paddle_speed, paddle_xsize, paddle_ysize, ball_speed, ball_radius)

    async def matching_on(self, event):
        game_users = event['game_users']
        now_players = event['now_players']

        text_data = json.dumps({
            'type': 'matching_on',
            'game_users': game_users,
            'now_players': now_players,
            # 'now_player': now_players,
        })
        await self.send(text_data=text_data)

    async def game_end(self, event):
        winner = event['winner']
        

        text_data = json.dumps({
            'type': 'ending',
            'winner': winner[0],
        })
        await self.send(text_data=text_data)

    async def next_game(self, event):
        now_players = event['now_players']

        text_data = json.dumps({
            'type': 'next_game',
            'now_players': now_players,
        })
        await self.send(text_data=text_data)
        

    async def finish(self, event):
        result = event['result']
        
        text_data = json.dumps({
            'type': 'finish',
            'result': result,
        })
        await self.send(text_data=text_data)

    async def chat_send(self, event):
        username = event['username'] 
        message = event['message']
        text_data = json.dumps({
            'type': 'chat',
            'username': username,
            'message': message,
        })
        await self.send(text_data=text_data)
        
