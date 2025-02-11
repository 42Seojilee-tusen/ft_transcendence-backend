from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from . import views

router = DefaultRouter()
router.register(r'me', views.MatchAuthViewSet, basename='my-game-records')
router.register(r'', views.MatchViewSet, basename='game-records')

urlpatterns = [
    path('', include(router.urls)),
]
