# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path("ws/game/battle/", consumers.GameBattleConsumer.as_asgi()),
    re_path("ws/game/tournament", consumers.GameTournamentConsumer.as_asgi()),
]