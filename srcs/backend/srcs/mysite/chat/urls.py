from django.urls import path
from . import views

urlpatterns = [
    # csrf토큰 발급용 api
    path('', views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
]