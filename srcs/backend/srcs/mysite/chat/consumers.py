# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
import uuid

import logging
logger = logging.getLogger('chat') 

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

class GameBattleConsumer(AsyncWebsocketConsumer):
    active_users = {}
    waiting_users = []
    
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = None
        try:
            if self.user is None or isinstance(self.user, AnonymousUser):
                logger.error("User not authenticated")
                raise Exception('User not authenticated')
            self.active_users[self.channel_name] = self.active_users.get(self.channel_name, 0) + 1
            # if self.channel_name in self.active_users and self.active_users[self.channel_name] > 1:
            #     logger.error(f"{self.user.username} is multi client error")
            #     raise Exception('multi client error')
            await self.accept()
            self.waiting_users.append({'channel_name': self.channel_name, 'user': self.user})
            if len(self.waiting_users) >= 2:
                user1 = self.waiting_users.pop(0)
                user2 = self.waiting_users.pop(0)
                self.group_name = f"group_{uuid.uuid4().hex}"
                await self.channel_layer.group_add(self.group_name, user1['channel_name'])
                await self.channel_layer.group_add(self.group_name, user2['channel_name'])
                await self.channel_layer.group_send(
                    self.group_name, {'type':'matching.on', "message": "매칭이 잡혔습니다", "group_name": self.group_name}
                )
        except Exception as e:
            logger.error(str(e))
            await self.close(code=4001)
            return 

    async def disconnect(self, close_code):
        if self.channel_name and self.channel_name in self.active_users:
            self.active_users[self.channel_name] -= 1
            if self.group_name:
                await self.channel_layer.group_send(
                    self.group_name, {'type':'matching.off', "message": "매칭이 끊겼습니다"}
                )
                await self.channel_layer.group_discard(self.group_name, self.channel_name)
                self.group_name = None
            for i, user in enumerate(self.waiting_users):
                if user['channel_name'] == self.channel_name:
                    del self.waiting_users[i]
                    break  # 일치하는 유저를 찾았으면 반복 종료
            if self.active_users[self.channel_name] <= 0:
                self.active_users.pop(self.channel_name, None)
        logger.debug("close_code: " + str(close_code))

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("message"):
            message = f"{self.username}: {data.get("message")}"
            await self.send(text_data=json.dumps({"message": message}))

    async def matching_on(self, event):
        message = event['message']
        self.group_name = event['group_name']
        await self.send(text_data=json.dumps({"message": message}))

    async def matching_off(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({"message": message}))