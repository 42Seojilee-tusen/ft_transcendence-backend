"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# mysite/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from utils.channelsmiddleware import JWTAuthMiddlewareStack

from chat.routing import websocket_urlpatterns as game_websocket
from online_status.routing import websocket_urlpatterns as online_websocket

combine_websocker_urlpatterns = game_websocket + online_websocket

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.

application = ProtocolTypeRouter({
    "http": django_asgi_app,
	"websocket": AllowedHostsOriginValidator(
		# AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
		JWTAuthMiddlewareStack(URLRouter(combine_websocker_urlpatterns))
	),
    # Just HTTP for now. (We can add other protocols later.)
})