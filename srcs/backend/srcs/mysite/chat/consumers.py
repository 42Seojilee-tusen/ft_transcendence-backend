# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
import uuid
from django.contrib.auth.models import AnonymousUser

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
    async def connect(self):
        self.user = self.scope["user"]
        self.username = None
        
        logger.debug("connect test")
        try:
            if self.user is None or isinstance(self.user, AnonymousUser):
                logger.debug("=" * 10)
                logger.debug("User not authenticated")
                logger.debug("=" * 10)
                raise Exception('User not authenticated')
            self.username = self.user.username
            if self.active_users[self.username] == True:
                raise Exception('multi client error')
            self.active_users[self.username] = True
            await self.accept()
        except Exception as e:
            logger.error(str(e))
            await self.close(code=4001)

    async def disconnect(self, close_code):
        if not self.username is None:
            del self.active_users[self.username]

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
            
        if data.get("message"):
            message = f"{self.username}: {data.get("message")}"
            await self.send(text_data=json.dumps({"message": message}))
