# chat/routing.py
from django.urls import re_path

from . import consumers
from . import tournamentconsumer

websocket_urlpatterns = [
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path("ws/game/battle/", consumers.GameBattleConsumer.as_asgi()),
    re_path("ws/game/tournament", tournamentconsumer.GameTournamentConsumer.as_asgi()),
]