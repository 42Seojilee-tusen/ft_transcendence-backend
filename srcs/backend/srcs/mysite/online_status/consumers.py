from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

import json
import logging
logger = logging.getLogger('chat') 

class OnlineUserConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = "online_user_group"
        try:
            # 유저 객체가 없거나, JWT토큰 인증이 안된 클라이언트 라면 에러를 던짐.
            if self.user is None or isinstance(self.user, AnonymousUser):
                logger.error("User not authenticated")
                raise Exception('User not authenticated')

            # 유저의 수를 증가
            self.active_channels[self.user.id] = self.active_channels.get(self.user.id, 0) + 1
            
            # # 내이름을 가진 유저의 수가 1명 이상이면 에러를 던짐 => 멀티 클라이언트
            # if self.channel_name in self.active_channels and self.active_channels[self.channel_name] > 1:
            #     logger.error(f"{self.user.username} is multi client error")
            #     raise Exception('multi client error')
            
            # 웹소켓 접속을 수락
            await self.accept()

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_send(
                self.group_name, {
                    'type':'broadcast_online_users',
                    'username': self.user.username
                }
            )
        except Exception as e:
            logger.error(str(e))
            await self.close(code=4001)
            return
    async def disconnect(self, close_code):
        if self.user is None or isinstance(self.user, AnonymousUser):
            logger.error(f"JWT인증이 안된 유저입니다.")
            return
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.group_name, {
                'type':'broadcast_online_users',
                'username': self.user.username
            }
        )
    async def receive(self, text_data):
        pass
    
    async def broadcast_online_users(self, event):
        username = event['username']
        text_data = json.dumps({
            'type': 'broadcast',
            'username': username
        })
        await self.send(text_data=text_data)
