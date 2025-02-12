# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from chat.match import MatchManager
import uuid

import logging
logger = logging.getLogger('chat') 

class GameBattleConsumer(AsyncWebsocketConsumer):
    # 접속한 클라이언트 수
    # id: 수
    active_users = {}

    # 게임 대기중인 유저
    # 채널이름, 유저 객체
    match_manager = MatchManager()
    
    async def connect(self):
        self.user = self.scope["user"]
        # 게임 참가를 위한 그룹이름
        self.group_name = None
        try:
            # 유저 객체가 없거나, JWT토큰 인증이 안된 클라이언트 라면 에러를 던짐.
            if self.user is None or isinstance(self.user, AnonymousUser):
                logger.error("User not authenticated")
                raise Exception('User not authenticated')
            # 유저의 수를 증가
            self.active_users[self.user.id] = self.active_users.get(self.user.id, 0) + 1
            # 내이름을 가진 유저의 수가 1명 이상이면 에러를 던짐 => 멀티 클라이언트
            # if self.channel_name in self.active_users and self.active_users[self.channel_name] > 1:
            #     logger.error(f"{self.user.username} is multi client error")
            #     raise Exception('multi client error')
            
            # 웹소켓 접속을 수락
            await self.accept()
            
            matching_user = self.match_manager.matching()
            # 매칭이 되면 그룹 생성
            if matching_user:
                self.group_name = f"group_{uuid.uuid4().hex}"
                logger.debug("="*20)
                logger.debug(self.group_name)
                logger.debug("="*20)
                
                await self.channel_layer.group_add(self.group_name, self.channel_name)
                await self.channel_layer.group_add(self.group_name, matching_user['channel_name'])
                await self.channel_layer.group_send(
                    self.group_name, {'type':'matching.on', "message": "매칭이 잡혔습니다", "group_name": self.group_name}
                )
            # 매칭이 안되면 대기중인 유저에 자신을 추가
            elif matching_user is None:
                self.match_manager.add_waiting(self.channel_name, self.user)

        except Exception as e:
            logger.error(str(e))
            await self.close(code=4001)
            return 

    async def disconnect(self, close_code):
        # JWT토큰 인증 오류 유저
        if self.user is None or isinstance(self.user, AnonymousUser):
            logger.error("등록이 안된 유저입니다.")
            return

        # 유저수를 1 감소
        # 만약 내가 마지막 유저였다면 해당 세트를 삭제
        self.active_users[self.user.id] -= 1
        if self.active_users[self.user.id] <= 0:
            self.active_users.pop(self.user.id, None)
        
        # 그룹이름이 존재한다면
        if self.group_name:
            # 매칭되어있던 유저들에게 접속을 종료했음을 알림
            await self.channel_layer.group_send(
                self.group_name, {'type':'matching.off', "message": "매칭이 끊겼습니다"}
            )
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            # 자신의 그룹 이름을 None으로 설정
            self.group_name = None

        # 대기중인 유저 목록에서 자기자신 제거
        self.match_manager.del_waiting(self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        if not data.get('type'):
            logger.debug("type is not define")
            return
        if data.get('type') == "chat":
            if self.group_name is None:
                return
            message = f"{data.get("message")}"
            data = {
                'type': 'chat.send',
                'username': self.user.username,
                'message': message
            }
            await self.channel_layer.group_send(
                self.group_name, data
            )

    async def matching_on(self, event):
        message = event['message']
        self.group_name = event['group_name']
        text_data = json.dumps({
            'username': 'system',
            'message': message,
        })
        await self.send(text_data=text_data)

    async def matching_off(self, event):
        message = event['message']
        text_data = json.dumps({
            'username': 'system',
            'message': message,
        })
        await self.send(text_data=text_data)

    async def chat_send(self, event):
        username = event['username'] 
        message = event['message']
        text_data = json.dumps({
            'username': username,
            'message': message,
        })
        await self.send(text_data=text_data)
